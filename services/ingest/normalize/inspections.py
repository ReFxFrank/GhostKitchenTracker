"""DOHMH snapshot → normalized frames.

The raw dataset is one row per VIOLATION CITATION; fields repeat across a
multi-violation inspection. This module dedupes to inspection level and splits
into establishments / inspections / violations frames (staging parquet, then
Postgres via load.py).

`1900-01-01` inspection dates mean permitted-but-never-inspected. Those rows
are kept for establishments (new kitchens are high-signal) but produce no
inspection or violation rows.

violation_description passes through VERBATIM. No trimming, no casing, no
truncation — brief §10.
"""

from __future__ import annotations

import polars as pl

import config
from normalize.names import normalize_dba
from normalize.phones import normalize_phone

SENTINEL_DATE = "1900-01-01"

INSPECTION_KEY = ["camis", "inspection_date", "inspection_type"]

_PLACEHOLDER_BIN_STRS = {str(b) for b in config.PLACEHOLDER_BINS}


def _date_col(name: str) -> pl.Expr:
    # Socrata floating timestamps: "2026-08-04T06:00:20.000" → date string.
    # Cast first: an all-null column may arrive as Null dtype, not Utf8.
    return pl.col(name).cast(pl.Utf8).str.slice(0, 10)


def prepare(df: pl.DataFrame) -> pl.DataFrame:
    """Trim timestamps to dates; leave everything else verbatim."""
    cols = {}
    for c in ("inspection_date", "grade_date", "record_date"):
        if c in df.columns:
            cols[c] = _date_col(c)
    return df.with_columns(**cols) if cols else df


def establishments_frame(df: pl.DataFrame) -> pl.DataFrame:
    """One row per CAMIS, latest-record-date values winning.

    Placeholder "million BINs" (1000000, 2000000, … — boro-code placeholders
    meaning "no specific building") are nulled: treating them as real BINs
    would collapse unrelated establishments into fake mega-buildings and
    poison the SHARED_BIN evidence family."""
    real = pl.col("inspection_date") != SENTINEL_DATE
    df = df.with_columns(
        pl.when(pl.col("bin").is_in(list(_PLACEHOLDER_BIN_STRS)))
        .then(pl.lit(None, dtype=pl.Utf8))
        .otherwise(pl.col("bin"))
        .alias("bin")
    )
    out = (
        df.sort("record_date")
        .group_by("camis")
        .agg(
            pl.col("dba").drop_nulls().last().alias("dba_raw"),
            pl.col("boro").drop_nulls().last(),
            pl.col("building").drop_nulls().last(),
            pl.col("street").drop_nulls().last(),
            pl.col("zipcode").drop_nulls().last(),
            pl.col("phone").drop_nulls().last(),
            pl.col("cuisine_description").drop_nulls().last().alias("cuisine"),
            pl.col("bin").drop_nulls().last(),
            pl.col("bbl").drop_nulls().last(),
            pl.col("latitude").drop_nulls().last(),
            pl.col("longitude").drop_nulls().last(),
            pl.col("inspection_date").filter(real).min().alias("first_seen"),
            pl.col("record_date").max().alias("last_seen"),
            (pl.col("inspection_date") == SENTINEL_DATE).any().alias("never_inspected"),
        )
        .with_columns(
            pl.col("dba_raw")
            .map_elements(normalize_dba, return_dtype=pl.Utf8)
            .alias("dba_normalized"),
            pl.col("phone")
            .map_elements(normalize_phone, return_dtype=pl.Utf8)
            .alias("phone_normalized"),
        )
    )
    return out


def inspections_frame(df: pl.DataFrame) -> pl.DataFrame:
    """Dedupe violation-level rows to one row per inspection."""
    return (
        df.filter(pl.col("inspection_date") != SENTINEL_DATE)
        .group_by(INSPECTION_KEY)
        .agg(
            pl.col("action").drop_nulls().first(),
            pl.col("score").drop_nulls().first(),
            pl.col("grade").drop_nulls().first(),
            pl.col("grade_date").drop_nulls().first(),
        )
        .sort(INSPECTION_KEY)
    )


def violations_frame(df: pl.DataFrame) -> pl.DataFrame:
    """One row per cited violation, keyed to its inspection. Verbatim text."""
    return (
        df.filter(
            (pl.col("inspection_date") != SENTINEL_DATE)
            & pl.col("violation_code").is_not_null()
        )
        .select(
            *INSPECTION_KEY,
            pl.col("violation_code"),
            pl.col("violation_description").alias("description_verbatim"),
            pl.col("critical_flag"),
        )
        .unique(maintain_order=True)
    )


def normalize_snapshot(df: pl.DataFrame) -> dict[str, pl.DataFrame]:
    df = prepare(df)
    return {
        "establishments": establishments_frame(df),
        "inspections": inspections_frame(df),
        "violations": violations_frame(df),
    }


def pluto_frame(df: pl.DataFrame) -> pl.DataFrame:
    """PLUTO snapshot → typed frame keyed by integer BBL.

    The Socrata JSON API returns bbl as a decimal string ("2054800111.00000000");
    parse deliberately, never string-compare (docs/SOURCES.md).
    """
    return df.with_columns(
        pl.col("bbl").cast(pl.Float64).cast(pl.Int64),
        pl.col("bldgarea").cast(pl.Float64, strict=False).cast(pl.Int64, strict=False),
        pl.col("lotarea").cast(pl.Float64, strict=False).cast(pl.Int64, strict=False),
        pl.col("numfloors").cast(pl.Float64, strict=False),
        pl.col("unitstotal").cast(pl.Float64, strict=False).cast(pl.Int64, strict=False),
        pl.col("yearbuilt").cast(pl.Float64, strict=False).cast(pl.Int64, strict=False),
        pl.col("latitude").cast(pl.Float64, strict=False),
        pl.col("longitude").cast(pl.Float64, strict=False),
    ).unique(subset=["bbl"], keep="first")
