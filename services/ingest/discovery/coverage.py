"""The coverage gate — the project's cheapest kill test (brief §8 Phase 1).

For each seeded known virtual brand in data/registry/brands/, does a matching
record exist in the Overture places extract AT ALL? The output is a fraction
and a verdict band:

  >= 50%   proceed
  30-50%   proceed, but pull Foursquare OS Places as a supplement and re-measure
  < 30%    STOP. The name-gap method has no path. Do not proceed on hope.

Runs directly on the snapshot parquet — no database required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import polars as pl
import yaml
from rapidfuzz import fuzz, process

import config
from normalize.names import normalize_dba

FUZZY_THRESHOLD = 90.0


@dataclass
class BrandEntry:
    slug: str
    brand: str
    aliases: list[str] = field(default_factory=list)
    sourced: bool = True

    @property
    def variants(self) -> list[str]:
        seen: dict[str, None] = {}
        for v in [self.brand, *self.aliases]:
            n = normalize_dba(v)
            if n:
                seen.setdefault(n)
        return list(seen)


@dataclass
class BrandResult:
    entry: BrandEntry
    hit: bool
    matches: list[tuple[str, float, str]]  # (raw name, score, category)


def load_registry_brands(registry_dir: Path | None = None) -> list[BrandEntry]:
    brands_dir = (registry_dir or config.REGISTRY_DIR) / "brands"
    entries: list[BrandEntry] = []
    for path in sorted(brands_dir.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        if not isinstance(doc, dict) or "brand" not in doc:
            raise ValueError(f"{path}: not a valid brand file")
        entries.append(
            BrandEntry(
                slug=path.stem,
                brand=doc["brand"],
                aliases=list(doc.get("aliases") or []),
                sourced=bool(doc.get("sources")),
            )
        )
    if not entries:
        raise ValueError(f"no brand files found under {brands_dir}")
    return entries


def load_place_names(parquet_path: Path) -> pl.DataFrame:
    df = pl.read_parquet(parquet_path, columns=["name_raw", "category"])
    df = df.filter(pl.col("name_raw").is_not_null())
    return df.with_columns(
        pl.col("name_raw")
        .map_elements(normalize_dba, return_dtype=pl.Utf8)
        .alias("name_normalized")
    ).filter(pl.col("name_normalized").is_not_null())


def match_brands(
    entries: list[BrandEntry],
    places: pl.DataFrame,
    threshold: float = FUZZY_THRESHOLD,
) -> list[BrandResult]:
    normalized = places["name_normalized"].to_list()
    raw = places["name_raw"].to_list()
    categories = places["category"].to_list()
    norm_index: dict[str, int] = {}
    for i, n in enumerate(normalized):
        norm_index.setdefault(n, i)

    results: list[BrandResult] = []
    for entry in entries:
        matches: list[tuple[str, float, str]] = []
        for variant in entry.variants:
            # Exact normalized match first — cheap and unambiguous.
            if variant in norm_index:
                i = norm_index[variant]
                matches.append((raw[i], 100.0, categories[i] or ""))
                continue
            for _, score, i in process.extract(
                variant,
                normalized,
                scorer=fuzz.token_set_ratio,
                score_cutoff=threshold,
                limit=3,
            ):
                matches.append((raw[i], float(score), categories[i] or ""))
        # Dedupe by raw name, best score first.
        best: dict[str, tuple[str, float, str]] = {}
        for m in sorted(matches, key=lambda m: -m[1]):
            best.setdefault(m[0], m)
        top = list(best.values())[:5]
        results.append(BrandResult(entry=entry, hit=bool(top), matches=top))
    return results


def verdict(pct: float) -> str:
    if pct >= 50:
        return "PROCEED — name-gap method viable (>=50% of known brands present)"
    if pct >= 30:
        return (
            "MARGINAL — proceed only after pulling Foursquare OS Places as a "
            "supplement and re-measuring; document the ceiling in METHODOLOGY.md"
        )
    return (
        "STOP — <30% of known virtual brands appear in place data. The name-gap "
        "method has no path. Do not proceed to Phase 2 on hope (brief §8)."
    )


def run(parquet_path: Path, registry_dir: Path | None = None) -> dict:
    entries = load_registry_brands(registry_dir)
    unsourced = [e.slug for e in entries if not e.sourced]
    places = load_place_names(parquet_path)
    results = match_brands(entries, places)
    hits = sum(1 for r in results if r.hit)
    pct = 100.0 * hits / len(results)
    return {
        "total_brands": len(results),
        "hits": hits,
        "pct": pct,
        "verdict": verdict(pct),
        "unsourced_brands": unsourced,
        "results": results,
    }
