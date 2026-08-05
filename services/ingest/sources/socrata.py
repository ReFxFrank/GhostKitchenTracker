"""Socrata fetcher: paginated, resumable, schema-drift-fatal.

Anti-slop guardrail (brief §10): if the upstream dataset changes shape, this
module raises before fetching a single row. No defensive defaults, no quietly
empty datasets.
"""

from __future__ import annotations

import datetime as dt
import json
import time
from typing import Any

import httpx

import config
from snapshots import Snapshot, SnapshotError

DEFAULT_PAGE_SIZE = 10_000
RETRY_STATUS = {429, 500, 502, 503, 504}
BACKOFF_SECONDS = [2, 4, 8, 16, 32]
# Never resume an interrupted fetch older than this — NYC Open Data refreshes
# daily (~06:00Z observed) and offset pagination across a refresh corrupts.
RESUME_MAX_AGE_HOURS = 12


class SchemaDriftError(RuntimeError):
    pass


def client() -> httpx.Client:
    headers = {"Accept": "application/json"}
    if config.SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = config.SOCRATA_APP_TOKEN
    return httpx.Client(base_url=config.SOCRATA_BASE, headers=headers, timeout=120.0)


def fetch_metadata_fields(dataset_id: str, http: httpx.Client) -> set[str]:
    resp = http.get(f"/api/views/{dataset_id}.json")
    resp.raise_for_status()
    cols = resp.json().get("columns", [])
    return {c["fieldName"] for c in cols if not c["fieldName"].startswith(":")}


def assert_no_drift(dataset_id: str, expected: set[str], actual: set[str]) -> None:
    missing = sorted(expected - actual)
    if missing:
        raise SchemaDriftError(
            f"dataset {dataset_id}: expected columns missing from live catalog: "
            f"{missing}. Upstream schema drifted — refusing to fetch. "
            "Verify against the catalog and update the source module deliberately."
        )


def _get_with_retries(http: httpx.Client, url: str, params: dict[str, Any]) -> httpx.Response:
    last: Exception | None = None
    for i, backoff in enumerate([0] + BACKOFF_SECONDS):
        if backoff:
            time.sleep(backoff)
        try:
            resp = http.get(url, params=params)
            if resp.status_code in RETRY_STATUS:
                last = RuntimeError(f"HTTP {resp.status_code} from {url}")
                continue
            resp.raise_for_status()
            return resp
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            last = exc
            continue
    raise RuntimeError(f"giving up after {len(BACKOFF_SECONDS) + 1} attempts: {last}")


def fetch_to_snapshot(
    *,
    dataset_id: str,
    source_name: str,
    expected_fields: set[str],
    select: list[str] | None = None,
    where: str | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int | None = None,
    snapshot: Snapshot | None = None,
) -> Snapshot:
    """Fetch a full dataset into a dated snapshot. Resumes an interrupted fetch
    for the same source+date; refuses to touch a completed one."""
    snap = snapshot or Snapshot(source_name)
    if snap.is_complete():
        if snap.is_partial():
            raise SnapshotError(
                f"a PARTIAL smoke-test snapshot occupies {snap.dir}; delete that "
                "directory (or point SEANCE_DATA_DIR elsewhere for smoke tests) "
                "before running the real fetch"
            )
        raise SnapshotError(
            f"snapshot {snap.dir} already complete; today's data is already on disk"
        )

    # A resumed fetch must be THE SAME fetch: identical dataset and query
    # params. Welding two different fetches into one "complete" snapshot would
    # be silent corruption, so params are pinned on first write and compared.
    fetch_params = {
        "dataset_id": dataset_id,
        "select": select,
        "where": where,
        "page_size": page_size,
        "order": ":id",
    }
    params_path = snap.dir / "fetch_params.json"

    # Resume validation is disk-only and happens BEFORE any network I/O:
    # a resumed fetch must be THE SAME fetch — identical dataset and query
    # params, AND against the same dataset state. Offset pagination against a
    # source that refreshed in between skips/duplicates rows; either way two
    # different fetches would be welded into one "complete" snapshot.
    pages = snap.existing_pages()
    offset = 0
    if pages:
        if not params_path.exists():
            raise SnapshotError(
                f"{snap.dir} has pages but no fetch_params.json; cannot prove "
                "the interrupted fetch used the same query — delete the "
                "directory and refetch"
            )
        on_disk = json.loads(params_path.read_text())
        started_at = on_disk.pop("started_at", None)
        if on_disk != fetch_params:
            raise SnapshotError(
                f"resume refused: {snap.dir} was started with different fetch "
                f"params ({on_disk}) than this invocation "
                f"({fetch_params}); delete the directory or match the params"
            )
        age_hours = None
        if started_at:
            started = dt.datetime.fromisoformat(started_at)
            age_hours = (dt.datetime.now(dt.timezone.utc) - started).total_seconds() / 3600
        if age_hours is None or age_hours > RESUME_MAX_AGE_HOURS:
            raise SnapshotError(
                f"resume refused: the interrupted fetch in {snap.dir} is "
                f"{'unstamped' if age_hours is None else f'{age_hours:.1f}h old'} "
                f"(limit {RESUME_MAX_AGE_HOURS}h). Socrata datasets refresh daily; "
                "resuming across a refresh skips or duplicates rows. Delete the "
                "directory and refetch."
            )
        offset = sum(1 for _ in _iter_page_lines(pages))
    page_index = len(pages)

    http = client()
    try:
        assert_no_drift(dataset_id, expected_fields, fetch_metadata_fields(dataset_id, http))

        url = f"/resource/{dataset_id}.json"
        total = offset
        fetched_pages = 0
        partial = False
        wrote_params = params_path.exists()
        while True:
            if max_pages is not None and fetched_pages >= max_pages:
                partial = True
                break
            params: dict[str, Any] = {
                "$limit": page_size,
                "$offset": offset,
                "$order": ":id",
            }
            if select:
                params["$select"] = ",".join(select)
            if where:
                params["$where"] = where
            rows = _get_with_retries(http, url, params).json()
            if not rows:
                break
            snap.write_page(page_index, rows)
            if not wrote_params:
                params_path.write_text(
                    json.dumps(
                        {
                            **fetch_params,
                            "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                        },
                        indent=2,
                    )
                )
                wrote_params = True
            total += len(rows)
            offset += len(rows)
            page_index += 1
            fetched_pages += 1
            if len(rows) < page_size:
                break

        snap.finalize(
            {
                "dataset_id": dataset_id,
                "endpoint": f"{config.SOCRATA_BASE}{url}",
                "select": select,
                "where": where,
                "page_size": page_size,
                "rows": total,
                "pages": page_index,
                "partial": partial,
                "app_token_used": config.SOCRATA_APP_TOKEN is not None,
            }
        )
        return snap
    finally:
        http.close()


def _iter_page_lines(pages: list) -> Any:
    import gzip

    for page in pages:
        with gzip.open(page, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield line
