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


def load_place_names(parquet_paths: Path | list[Path]) -> pl.DataFrame:
    paths = [parquet_paths] if isinstance(parquet_paths, Path) else list(parquet_paths)
    frames = []
    for p in paths:
        df = pl.read_parquet(p, columns=["name_raw", "category"])
        frames.append(df.filter(pl.col("name_raw").is_not_null()))
    df = pl.concat(frames, how="vertical")
    return df.with_columns(
        pl.col("name_raw")
        .map_elements(normalize_dba, return_dtype=pl.Utf8)
        .alias("name_normalized")
    ).filter(pl.col("name_normalized").is_not_null())


def _strip_the(s: str) -> str:
    return " ".join(t for t in s.split() if t != "the")


# A subset hit tolerates at most this many extra tokens in the place name:
# "nice day chinese" is a hit for brand "nice day"; "have a nice day cafe" is not.
SUBSET_EXTRA_TOKENS_MAX = 2


def match_brands(
    entries: list[BrandEntry],
    places: pl.DataFrame,
    threshold: float = FUZZY_THRESHOLD,
) -> list[BrandResult]:
    """Presence semantics, deliberately directional: a brand is present when a
    place name IS the brand, CONTAINS the brand's tokens (with a small extra-
    token allowance), or is a near-typo of it. A place name that is merely a
    token-subset of the brand ("Monster" for "Monster Mac") is NOT a hit —
    token_set_ratio alone would score that 100, which is why it isn't used."""
    normalized = places["name_normalized"].to_list()
    raw = places["name_raw"].to_list()
    categories = places["category"].to_list()
    stripped = [_strip_the(n) for n in normalized]
    norm_index: dict[str, int] = {}
    for i, n in enumerate(stripped):
        norm_index.setdefault(n, i)

    results: list[BrandResult] = []
    for entry in entries:
        matches: list[tuple[str, float, str]] = []
        for variant in entry.variants:
            v = _strip_the(variant)
            vtok = set(v.split())
            # 1. Exact normalized match ("the"-insensitive) — unambiguous.
            if v in norm_index:
                i = norm_index[v]
                matches.append((raw[i], 100.0, categories[i] or ""))
                continue
            # 2. Directional token containment: brand tokens ⊆ place tokens.
            #    token_set_ratio == 100 iff one token set contains the other;
            #    the direction filter and extra-token cap are applied after.
            for _, score, i in process.extract(
                v, stripped, scorer=fuzz.token_set_ratio, score_cutoff=100, limit=25
            ):
                ptok = set(stripped[i].split())
                if vtok <= ptok and len(ptok - vtok) <= SUBSET_EXTRA_TOKENS_MAX:
                    matches.append((raw[i], float(score), categories[i] or ""))
            # 3. Near-typo variants (no subset freebie in token_sort_ratio).
            for _, score, i in process.extract(
                v, stripped, scorer=fuzz.token_sort_ratio, score_cutoff=threshold, limit=3
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


def run(parquet_paths: Path | list[Path], registry_dir: Path | None = None) -> dict:
    entries = load_registry_brands(registry_dir)
    unsourced = [e.slug for e in entries if not e.sourced]
    places = load_place_names(parquet_paths)
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
