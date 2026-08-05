"""Overture Maps places — the other half of the name-gap diff.

Pulls the NYC bbox from the PINNED release via DuckDB with bbox pushdown; no
planet download. Schema is introspected live and required columns asserted
before the extract runs — drift fails loudly (brief §10).

Live schema notes (verified 2026-08-05 against release 2026-07-22.0):
- `operating_status` exists (VARCHAR).
- `sources` is a list of structs carrying a per-source `license` — this feeds
  places.source_license (NOT NULL) directly.
- Coordinates come from the bbox struct midpoint (points have xmin == xmax),
  which avoids needing the spatial extension for the extract.

Proxy note: this environment (and any environment with an intercepting
proxy that injects placeholder AWS credentials) breaks anonymous S3 access —
DuckDB signs with the junk creds and S3 returns 403. We strip AWS_* env vars
around the connection; the bucket is public.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Any

import duckdb

import config
from snapshots import Snapshot, SnapshotError

SOURCE = "overture"
PARQUET_NAME = "nyc_places.parquet"

REQUIRED_COLUMNS = {
    "id", "names", "categories", "confidence", "operating_status", "phones",
    "websites", "socials", "addresses", "brand", "sources", "bbox",
}


class OvertureSchemaError(RuntimeError):
    pass


@contextlib.contextmanager
def _anonymous_aws_env():
    saved = {}
    for var in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        if var in os.environ:
            saved[var] = os.environ.pop(var)
    try:
        yield
    finally:
        os.environ.update(saved)


def _connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        con.execute(f"SET http_proxy='{proxy}'")
        ca = os.environ.get("AWS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
        if os.path.exists(ca):
            con.execute(f"SET ca_cert_file='{ca}'")
    con.execute("SET s3_region='us-west-2'")
    return con


def assert_schema(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    rows = con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{config.OVERTURE_S3}', hive_partitioning=1) LIMIT 0"
    ).fetchall()
    actual = {name: typ for name, typ, *_ in rows}
    missing = sorted(REQUIRED_COLUMNS - set(actual))
    if missing:
        raise OvertureSchemaError(
            f"Overture release {config.OVERTURE_RELEASE}: required columns missing "
            f"from live schema: {missing}. Refusing to extract."
        )
    return actual


def fetch(
    bbox: dict[str, float] = config.NYC_BBOX,
    limit: int | None = None,
    snapshot: Snapshot | None = None,
) -> Snapshot:
    snap = snapshot or Snapshot(SOURCE)
    if snap.is_complete():
        raise SnapshotError(f"snapshot {snap.dir} already complete")
    snap.write_file_placeholder()
    out = snap.dir / PARQUET_NAME

    limit_clause = f"LIMIT {int(limit)}" if limit else ""
    sql = f"""
    COPY (
      SELECT
        id,
        names."primary"        AS name_raw,
        categories."primary"   AS category,
        basic_category,
        confidence,
        operating_status,
        phones,
        websites,
        socials,
        addresses[1].freeform  AS address_freeform,
        addresses[1].postcode  AS postcode,
        addresses[1].locality  AS locality,
        brand.names."primary"  AS brand_name,
        list_sort(list_distinct(list_transform(
            sources, s -> coalesce(s.license, 'unspecified')
        )))                    AS source_licenses,
        (bbox.xmin + bbox.xmax) / 2 AS lng,
        (bbox.ymin + bbox.ymax) / 2 AS lat
      FROM read_parquet('{config.OVERTURE_S3}', hive_partitioning=1)
      WHERE bbox.xmin > {bbox["xmin"]} AND bbox.xmax < {bbox["xmax"]}
        AND bbox.ymin > {bbox["ymin"]} AND bbox.ymax < {bbox["ymax"]}
      {limit_clause}
    ) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """

    with _anonymous_aws_env():
        con = _connect()
        try:
            live_schema = assert_schema(con)
            con.execute(sql)
            rows = con.execute(f"SELECT count(*) FROM read_parquet('{out}')").fetchone()[0]
        finally:
            con.close()

    snap.finalize(
        {
            "release": config.OVERTURE_RELEASE,
            "s3_path": config.OVERTURE_S3,
            "bbox": bbox,
            "limit": limit,
            "rows": rows,
            "file": PARQUET_NAME,
            "live_schema_columns": sorted(live_schema),
            "partial": limit is not None,
        }
    )
    return snap


def parquet_path(snap: Snapshot) -> Path:
    return snap.dir / PARQUET_NAME
