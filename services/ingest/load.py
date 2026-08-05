"""Staging parquet → Postgres.

Idempotency contract (Phase 1 acceptance: running twice produces zero
duplicate rows):
- buildings, establishments, places: natural-key UPSERTs.
- inspections + violations: replace-all per load. The raw snapshot is the
  durable record; these tables are a projection of it, and replace-all is the
  simplest strategy that cannot drift. (brand_links reference camis/bin, never
  inspection ids, so replacement is safe.)

Canonical address note: until Geosupport is installed (VPS, Phase 1 tail),
canonical_address is the raw DOHMH building+street+zipcode concatenation.
Geosupport gets wired into THIS loader (not applied as a one-off fix) so that
weekly upserts keep producing canonical values rather than reverting them.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

import config
import db
from normalize.names import normalize_dba
from normalize.phones import normalize_phone


def _staging(date: str) -> Path:
    return config.STAGING_DIR / date


def load_buildings(conn, est: pl.DataFrame, pluto: pl.DataFrame | None) -> int:
    b = (
        est.filter(pl.col("bin").is_not_null())
        # Defense in depth: normalize nulls placeholder BINs already, but a
        # fake mega-building must never be creatable from any staging input.
        .filter(~pl.col("bin").cast(pl.Int64).is_in(sorted(config.PLACEHOLDER_BINS)))
        .with_columns(
            pl.col("bin").cast(pl.Int64),
            pl.col("bbl").cast(pl.Float64, strict=False).cast(pl.Int64, strict=False),
            # (0,0) is failed-geocode junk, not a coordinate. Null it BEFORE the
            # aggregation so drop_nulls().first() can still pick a real sibling
            # coordinate at the same BIN.
            pl.when(
                (pl.col("latitude").cast(pl.Float64, strict=False) == 0.0)
                & (pl.col("longitude").cast(pl.Float64, strict=False) == 0.0)
            )
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("latitude").cast(pl.Float64, strict=False))
            .alias("latitude"),
            pl.when(
                (pl.col("latitude").cast(pl.Float64, strict=False) == 0.0)
                & (pl.col("longitude").cast(pl.Float64, strict=False) == 0.0)
            )
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("longitude").cast(pl.Float64, strict=False))
            .alias("longitude"),
            pl.concat_str(
                [pl.col("building"), pl.col("street"), pl.col("zipcode")],
                separator=" ",
                ignore_nulls=True,
            ).alias("canonical_address"),
        )
        .group_by("bin")
        .agg(
            pl.col("bbl").drop_nulls().first(),
            pl.col("latitude").drop_nulls().first().alias("lat"),
            pl.col("longitude").drop_nulls().first().alias("lng"),
            pl.col("boro").drop_nulls().first(),
            pl.col("canonical_address").drop_nulls().first(),
        )
    )
    if pluto is not None:
        b = b.join(
            pluto.select(
                "bbl", "bldgclass", "bldgarea", "numfloors", "ownername", "yearbuilt"
            ),
            on="bbl",
            how="left",
        )
    else:
        b = b.with_columns(
            pl.lit(None, dtype=pl.Utf8).alias("bldgclass"),
            pl.lit(None, dtype=pl.Int64).alias("bldgarea"),
            pl.lit(None, dtype=pl.Float64).alias("numfloors"),
            pl.lit(None, dtype=pl.Utf8).alias("ownername"),
            pl.lit(None, dtype=pl.Int64).alias("yearbuilt"),
        )
    b = b.with_columns(
        pl.col("bldgclass").str.slice(0, 1).alias("bldg_class_group")
    )

    # COALESCE on enrichment columns: fresh PLUTO data wins, but a load run
    # without pluto.parquet must not null out enrichment loaded earlier.
    # (0,0) coordinates are DOHMH null-island junk, never a real NYC location.
    sql = """
    INSERT INTO buildings (bin, bbl, lat, lng, geom, boro, canonical_address,
                           bldg_class, bldg_class_group, bldg_area, num_floors,
                           owner_name, year_built)
    VALUES (%(bin)s, %(bbl)s, %(lat)s, %(lng)s,
            CASE WHEN %(lng)s IS NULL OR %(lat)s IS NULL
                      OR (%(lng)s = 0 AND %(lat)s = 0) THEN NULL
                 ELSE ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326) END,
            %(boro)s, %(canonical_address)s, %(bldgclass)s, %(bldg_class_group)s,
            %(bldgarea)s, %(numfloors)s, %(ownername)s, %(yearbuilt)s)
    ON CONFLICT (bin) DO UPDATE SET
      bbl = COALESCE(EXCLUDED.bbl, buildings.bbl),
      lat = COALESCE(EXCLUDED.lat, buildings.lat),
      lng = COALESCE(EXCLUDED.lng, buildings.lng),
      geom = COALESCE(EXCLUDED.geom, buildings.geom),
      boro = COALESCE(EXCLUDED.boro, buildings.boro),
      canonical_address = COALESCE(EXCLUDED.canonical_address, buildings.canonical_address),
      bldg_class = COALESCE(EXCLUDED.bldg_class, buildings.bldg_class),
      bldg_class_group = COALESCE(EXCLUDED.bldg_class_group, buildings.bldg_class_group),
      bldg_area = COALESCE(EXCLUDED.bldg_area, buildings.bldg_area),
      num_floors = COALESCE(EXCLUDED.num_floors, buildings.num_floors),
      owner_name = COALESCE(EXCLUDED.owner_name, buildings.owner_name),
      year_built = COALESCE(EXCLUDED.year_built, buildings.year_built)
    """
    rows = b.to_dicts()
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_establishments(conn, est: pl.DataFrame) -> int:
    e = est.with_columns(
        pl.col("camis").cast(pl.Int64),
        pl.col("bin").cast(pl.Int64, strict=False),
    )
    sql = """
    INSERT INTO establishments (camis, bin, dba_raw, dba_normalized,
                                phone_normalized, cuisine, first_seen, last_seen, status)
    VALUES (%(camis)s,
            CASE WHEN %(bin)s IN (SELECT bin FROM buildings) THEN %(bin)s END,
            %(dba_raw)s, %(dba_normalized)s, %(phone_normalized)s, %(cuisine)s,
            %(first_seen)s::date, %(last_seen)s::date, 'active')
    ON CONFLICT (camis) DO UPDATE SET
      bin = EXCLUDED.bin, dba_raw = EXCLUDED.dba_raw,
      dba_normalized = EXCLUDED.dba_normalized,
      phone_normalized = EXCLUDED.phone_normalized, cuisine = EXCLUDED.cuisine,
      -- DOHMH is a rolling window: old inspections age out, so this snapshot's
      -- minimum drifts forward. first_seen only ever moves BACKWARD.
      first_seen = LEAST(
        COALESCE(establishments.first_seen, EXCLUDED.first_seen),
        COALESCE(EXCLUDED.first_seen, establishments.first_seen)
      ),
      last_seen = GREATEST(
        COALESCE(establishments.last_seen, EXCLUDED.last_seen),
        COALESCE(EXCLUDED.last_seen, establishments.last_seen)
      ),
      status = EXCLUDED.status
    """
    cols = [
        "camis", "bin", "dba_raw", "dba_normalized", "phone_normalized",
        "cuisine", "first_seen", "last_seen",
    ]
    rows = e.select(cols).to_dicts()
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_inspections_violations(
    conn, insp: pl.DataFrame, viol: pl.DataFrame
) -> tuple[int, int]:
    insp = insp.with_columns(pl.col("camis").cast(pl.Int64))
    viol = viol.with_columns(pl.col("camis").cast(pl.Int64))
    with conn.cursor() as cur:
        # Replace-all guard: never trade a populated table for a suspiciously
        # small staging frame. A full DOHMH snapshot yields ~90k inspections;
        # replacing 90k rows with 200 means someone loaded smoke-test staging.
        existing = cur.execute("SELECT count(*) FROM inspections").fetchone()[0]
        if existing > 0 and len(insp) < existing * 0.5:
            raise RuntimeError(
                f"refusing replace-all: {existing} inspections in the DB but only "
                f"{len(insp)} in staging (<50%). This looks like partial/smoke-test "
                "staging. Re-run normalize from a full snapshot, or load that."
            )
        cur.execute("DELETE FROM violations")
        cur.execute("DELETE FROM inspections")
        cur.executemany(
            """
            INSERT INTO inspections (camis, inspected_at, action, score, grade, graded_at, type)
            VALUES (%(camis)s, %(inspection_date)s::date, %(action)s,
                    %(score)s::int, %(grade)s, %(grade_date)s::date, %(inspection_type)s)
            """,
            insp.to_dicts(),
        )
        cur.execute("SELECT id, camis, inspected_at::text, coalesce(type,'') FROM inspections")
        key_to_id = {(camis, d, t): i for i, camis, d, t in cur.fetchall()}

        v_rows = []
        for r in viol.to_dicts():
            key = (r["camis"], r["inspection_date"], r["inspection_type"] or "")
            inspection_id = key_to_id.get(key)
            if inspection_id is None:
                raise RuntimeError(
                    f"violation row has no parent inspection: {key} — "
                    "normalize/load invariant broken, refusing to continue"
                )
            v_rows.append(
                {
                    "inspection_id": inspection_id,
                    "code": r["violation_code"],
                    "description_verbatim": r["description_verbatim"],
                    "critical_flag": r["critical_flag"],
                }
            )
        cur.executemany(
            """
            INSERT INTO violations (inspection_id, code, description_verbatim, critical_flag)
            VALUES (%(inspection_id)s, %(code)s, %(description_verbatim)s, %(critical_flag)s)
            """,
            v_rows,
        )
    return len(insp), len(v_rows)


def load_places(conn, parquet: Path, source_release: str) -> int:
    df = pl.read_parquet(parquet)
    df = (
        df.filter(pl.col("name_raw").is_not_null())
        .with_columns(
            pl.col("name_raw")
            .map_elements(normalize_dba, return_dtype=pl.Utf8)
            .alias("name_normalized"),
            pl.col("phones").list.first().alias("phone_first"),
            pl.col("websites").list.first().alias("website"),
            pl.col("source_licenses").list.join("+").alias("source_license"),
        )
        .with_columns(
            pl.col("phone_first")
            .map_elements(normalize_phone, return_dtype=pl.Utf8)
            .alias("phone_normalized"),
        )
    )
    sql = """
    INSERT INTO places (gers_id, name_raw, name_normalized, category, confidence,
                        operating_status, phone_normalized, website, lat, lng, geom,
                        source_license, source_release)
    VALUES (%(id)s, %(name_raw)s, %(name_normalized)s, %(category)s, %(confidence)s,
            %(operating_status)s, %(phone_normalized)s, %(website)s, %(lat)s, %(lng)s,
            CASE WHEN %(lng)s IS NULL OR %(lat)s IS NULL THEN NULL
                 ELSE ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326) END,
            %(source_license)s, %(source_release)s)
    ON CONFLICT (gers_id) DO UPDATE SET
      name_raw = EXCLUDED.name_raw, name_normalized = EXCLUDED.name_normalized,
      category = EXCLUDED.category, confidence = EXCLUDED.confidence,
      operating_status = EXCLUDED.operating_status,
      phone_normalized = EXCLUDED.phone_normalized, website = EXCLUDED.website,
      lat = EXCLUDED.lat, lng = EXCLUDED.lng, geom = EXCLUDED.geom,
      source_license = EXCLUDED.source_license,
      source_release = EXCLUDED.source_release
    """
    cols = [
        "id", "name_raw", "name_normalized", "category", "confidence",
        "operating_status", "phone_normalized", "website", "lat", "lng",
        "source_license",
    ]
    rows = df.select(cols).with_columns(
        pl.lit(source_release).alias("source_release")
    ).to_dicts()
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_all(date: str, overture_parquet: Path | None = None,
             overture_release: str | None = None) -> dict[str, int]:
    staging = _staging(date)
    est = pl.read_parquet(staging / "establishments.parquet")
    insp = pl.read_parquet(staging / "inspections.parquet")
    viol = pl.read_parquet(staging / "violations.parquet")
    pluto_path = staging / "pluto.parquet"
    pluto = pl.read_parquet(pluto_path) if pluto_path.exists() else None

    counts: dict[str, int] = {}
    with db.connect() as conn:
        counts["buildings"] = load_buildings(conn, est, pluto)
        counts["establishments"] = load_establishments(conn, est)
        n_i, n_v = load_inspections_violations(conn, insp, viol)
        counts["inspections"], counts["violations"] = n_i, n_v
        if overture_parquet is not None:
            counts["places"] = load_places(
                conn, overture_parquet, overture_release or config.OVERTURE_RELEASE
            )
        conn.commit()
    return counts
