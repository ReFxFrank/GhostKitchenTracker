"""Immutable dated raw snapshots: data/raw/{source}/{YYYY-MM-DD}/.

Rules (brief §3):
- Every fetch writes a dated snapshot and is NEVER mutated afterwards.
- A snapshot with a manifest.json is complete and immutable; attempting to
  write into it is an error, not a warning.
- A snapshot without a manifest is a resumable in-progress fetch.
- Downstream stages read snapshots, never live sources.
"""

from __future__ import annotations

import datetime as dt
import gzip
import io
import json
import os
from pathlib import Path
from typing import Any, Iterator

import polars as pl

import config


class SnapshotError(RuntimeError):
    pass


def today_str() -> str:
    return dt.date.today().isoformat()


class Snapshot:
    def __init__(self, source: str, date: str | None = None, root: Path | None = None):
        self.source = source
        self.date = date or today_str()
        self.dir = (root or config.RAW_DIR) / source / self.date

    # -- state ---------------------------------------------------------------

    @property
    def manifest_path(self) -> Path:
        return self.dir / "manifest.json"

    def is_complete(self) -> bool:
        return self.manifest_path.exists()

    def is_partial(self) -> bool:
        return self.is_complete() and bool(self.manifest().get("partial"))

    def manifest(self) -> dict[str, Any]:
        return json.loads(self.manifest_path.read_text())

    def existing_pages(self) -> list[Path]:
        if not self.dir.exists():
            return []
        return sorted(self.dir.glob("page-*.jsonl.gz"))

    # -- writing -------------------------------------------------------------

    def _guard_mutable(self) -> None:
        if self.is_complete():
            raise SnapshotError(
                f"snapshot {self.dir} is complete and immutable; "
                "a new fetch belongs in a new dated directory"
            )

    def ensure_dir(self) -> None:
        self._guard_mutable()
        self.dir.mkdir(parents=True, exist_ok=True)

    def page_path(self, index: int) -> Path:
        return self.dir / f"page-{index:05d}.jsonl.gz"

    def write_page(self, index: int, rows: list[dict[str, Any]]) -> Path:
        self.ensure_dir()
        path = self.page_path(index)
        tmp = path.with_suffix(".tmp")
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
                f.write("\n")
        os.replace(tmp, path)
        return path

    def write_file_placeholder(self) -> None:
        """For non-paged snapshots (e.g. a single parquet) — just ensure the dir."""
        self.ensure_dir()

    def finalize(self, meta: dict[str, Any]) -> None:
        self._guard_mutable()
        manifest = {
            "source": self.source,
            "date": self.date,
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            **meta,
        }
        tmp = self.manifest_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(manifest, indent=2))
        os.replace(tmp, self.manifest_path)

    # -- reading -------------------------------------------------------------

    def _require_complete(self) -> None:
        if not self.is_complete():
            raise SnapshotError(
                f"snapshot {self.dir} has no manifest; refusing to read an "
                "in-progress fetch (resume or re-run the fetch first)"
            )

    def iter_rows(self) -> Iterator[dict[str, Any]]:
        self._require_complete()
        for page in self.existing_pages():
            with gzip.open(page, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)

    def read_frame(self) -> pl.DataFrame:
        """All pages as one polars frame, every column Utf8 (Socrata is stringly).

        Nested values (e.g. DOHMH's `location` struct) are JSON-encoded rather
        than dropped; all-null columns are cast from Null to Utf8 so downstream
        string ops never see a Null-dtype column."""
        self._require_complete()
        frames: list[pl.DataFrame] = []
        for page in self.existing_pages():
            with gzip.open(page, "rb") as f:
                data = f.read()
            if not data.strip():
                continue
            df = pl.read_ndjson(io.BytesIO(data), infer_schema_length=None)
            casts = []
            for name, dtype in df.schema.items():
                if isinstance(dtype, pl.Struct):
                    casts.append(pl.col(name).struct.json_encode().alias(name))
                elif isinstance(dtype, pl.List):
                    casts.append(
                        pl.col(name).cast(pl.List(pl.Utf8)).list.join(",").alias(name)
                    )
                elif dtype != pl.Utf8:
                    casts.append(pl.col(name).cast(pl.Utf8).alias(name))
            if casts:
                df = df.with_columns(casts)
            frames.append(df)
        if not frames:
            return pl.DataFrame()
        return pl.concat(frames, how="diagonal")

    @classmethod
    def latest_complete(
        cls, source: str, root: Path | None = None, include_partial: bool = False
    ) -> "Snapshot":
        """Latest complete snapshot. PARTIAL snapshots (smoke tests) are skipped
        unless explicitly requested — a smoke test must never silently become
        the default input to normalize/load."""
        base = (root or config.RAW_DIR) / source
        if not base.exists():
            raise SnapshotError(f"no snapshots exist for source '{source}' under {base}")
        for date_dir in sorted(base.iterdir(), reverse=True):
            snap = cls(source, date_dir.name, root=root)
            if snap.is_complete() and (include_partial or not snap.is_partial()):
                return snap
        raise SnapshotError(
            f"no COMPLETE non-partial snapshot for source '{source}' under {base}"
        )
