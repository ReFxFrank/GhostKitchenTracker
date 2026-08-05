"""Foursquare OS Places — the contingent coverage supplement (brief §8 Phase 1).

Activated because the 2026-08-05 preliminary coverage gate landed in the
30-50% MARGINAL band. Apache 2.0; attribution requires preserving Foursquare's
NOTICE.txt content (see docs/ATTRIBUTION.md).

ACCESS IS GATED (verified 2026-08-05): the S3 bucket no longer serves data
objects and the Hugging Face dataset returns 401 GatedRepo anonymously.
A free Hugging Face account that has accepted the dataset terms at
https://huggingface.co/datasets/foursquare/fsq-os-places is required; put its
token in HF_TOKEN. Zero dollars — but a human account action.

Because access is gated, the column list below is from FSQ documentation and
is NOT yet live-verified; the DESCRIBE assertion runs before the first real
extract and will fail loudly if the schema differs (that is the point).
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb

import config
from snapshots import Snapshot, SnapshotError

SOURCE = "fsq"
PARQUET_NAME = "nyc_places_fsq.parquet"

HF_GLOB = (
    "hf://datasets/foursquare/fsq-os-places/release/"
    f"dt={config.FSQ_RELEASE}/places/parquet/*.parquet"
)

REQUIRED_COLUMNS = {
    "fsq_place_id", "name", "latitude", "longitude", "address", "locality",
    "region", "postcode", "country", "tel", "website", "date_closed",
    "fsq_category_labels",
}


class FsqAccessError(RuntimeError):
    pass


class FsqSchemaError(RuntimeError):
    pass


def _connect() -> duckdb.DuckDBPyConnection:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise FsqAccessError(
            "HF_TOKEN is not set. The Foursquare OS Places dataset is gated: "
            "create a free Hugging Face account, accept the terms at "
            "https://huggingface.co/datasets/foursquare/fsq-os-places, and "
            "export HF_TOKEN. (Verified gated on 2026-08-05.)"
        )
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        con.execute(f"SET http_proxy='{proxy}'")
        ca = os.environ.get("AWS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
        if os.path.exists(ca):
            con.execute(f"SET ca_cert_file='{ca}'")
    con.execute(
        "CREATE SECRET hf_secret (TYPE huggingface, TOKEN ?)", [token]
    )
    return con


def assert_schema(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    rows = con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{HF_GLOB}') LIMIT 0"
    ).fetchall()
    actual = {name: typ for name, typ, *_ in rows}
    missing = sorted(REQUIRED_COLUMNS - set(actual))
    if missing:
        raise FsqSchemaError(
            f"FSQ OS Places release {config.FSQ_RELEASE}: expected columns missing "
            f"from live schema: {missing}. The documented schema drifted — update "
            "sources/fsq.py deliberately."
        )
    return actual


def fetch(
    bbox: dict[str, float] = config.NYC_BBOX,
    limit: int | None = None,
    snapshot: Snapshot | None = None,
) -> Snapshot:
    snap = snapshot or Snapshot(SOURCE)
    if snap.is_complete():
        if snap.is_partial():
            raise SnapshotError(
                f"a PARTIAL smoke-test snapshot occupies {snap.dir}; delete that "
                "directory (partial snapshots are disposable, not part of the "
                "durable record) or point SEANCE_DATA_DIR elsewhere"
            )
        raise SnapshotError(f"snapshot {snap.dir} already complete")
    snap.write_file_placeholder()
    out = snap.dir / PARQUET_NAME

    limit_clause = f"LIMIT {int(limit)}" if limit else ""
    sql = f"""
    COPY (
      SELECT
        fsq_place_id            AS id,
        name                    AS name_raw,
        fsq_category_labels[1]  AS category,
        NULL                    AS confidence,
        CASE WHEN date_closed IS NULL THEN 'open' ELSE 'closed' END AS operating_status,
        [tel]                   AS phones,
        [website]               AS websites,
        address                 AS address_freeform,
        postcode,
        locality,
        ['Apache-2.0']          AS source_licenses,
        longitude               AS lng,
        latitude                AS lat
      FROM read_parquet('{HF_GLOB}')
      WHERE country = 'US'
        AND longitude > {bbox["xmin"]} AND longitude < {bbox["xmax"]}
        AND latitude  > {bbox["ymin"]} AND latitude  < {bbox["ymax"]}
      {limit_clause}
    ) TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """

    con = _connect()
    try:
        live_schema = assert_schema(con)
        con.execute(sql)
        rows = con.execute(f"SELECT count(*) FROM read_parquet('{out}')").fetchone()[0]
    finally:
        con.close()

    snap.finalize(
        {
            "release": config.FSQ_RELEASE,
            "hf_path": HF_GLOB,
            "bbox": bbox,
            "limit": limit,
            "rows": rows,
            "file": PARQUET_NAME,
            "live_schema_columns": sorted(live_schema),
            "partial": limit is not None,
            "license": "Apache-2.0",
        }
    )
    return snap


def parquet_path(snap: Snapshot) -> Path:
    return snap.dir / PARQUET_NAME
