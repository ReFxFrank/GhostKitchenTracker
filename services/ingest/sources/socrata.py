"""Socrata fetcher: paginated, resumable, schema-drift-fatal.

Anti-slop guardrail (brief §10): if the upstream dataset changes shape, this
module raises before fetching a single row. No defensive defaults, no quietly
empty datasets.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

import config
from snapshots import Snapshot, SnapshotError

DEFAULT_PAGE_SIZE = 10_000
RETRY_STATUS = {429, 500, 502, 503, 504}
BACKOFF_SECONDS = [2, 4, 8, 16, 32]


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
        raise SnapshotError(
            f"snapshot {snap.dir} already complete; today's data is already on disk"
        )

    http = client()
    try:
        assert_no_drift(dataset_id, expected_fields, fetch_metadata_fields(dataset_id, http))

        # Resume: count rows already fetched; continue at that offset.
        pages = snap.existing_pages()
        offset = 0
        if pages:
            offset = sum(1 for _ in _iter_page_lines(pages))
        page_index = len(pages)

        url = f"/resource/{dataset_id}.json"
        total = offset
        fetched_pages = 0
        partial = False
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
