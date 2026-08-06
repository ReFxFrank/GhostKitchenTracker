import type { Brand, BrandMatch } from "../types";
import { normalizeName, tokenize } from "./normalize";

function jaccard(a: string[], b: string[]): number {
  if (a.length === 0 || b.length === 0) return 0;
  const setA = new Set(a);
  const setB = new Set(b);
  let overlap = 0;
  for (const t of setA) if (setB.has(t)) overlap++;
  return overlap / (setA.size + setB.size - overlap);
}

function nameConfidence(query: string, candidate: string): number {
  // Only true equality after normalization counts as an exact match (>= 0.85);
  // everything below lands in the fuzzy tier so the 35-point exact signal
  // can't fire off a partial name.
  if (query === candidate) return 1;

  const qTokens = tokenize(query);
  const cTokens = tokenize(candidate);

  // Token-boundary containment: every word of the shorter name appears as a
  // whole word in the longer ("flavortown" ⊂ "guy fieris flavortown kitchen").
  // Raw substring inclusion is not enough — "fuku" must not match "fukushima".
  if (query.length >= 4 && candidate.length >= 4) {
    const [shorter, longer] =
      qTokens.length <= cTokens.length ? [qTokens, cTokens] : [cTokens, qTokens];
    const longerSet = new Set(longer);
    if (shorter.length > 0 && shorter.every((t) => longerSet.has(t))) return 0.7;
  }

  const similarity = jaccard(qTokens, cTokens);
  return similarity >= 0.5 ? 0.5 + similarity * 0.3 : 0;
}

/**
 * Match a user-entered restaurant name against the brand database.
 * Returns matches sorted by confidence, best first.
 */
export function matchBrands(rawQuery: string, brands: Brand[]): BrandMatch[] {
  const query = normalizeName(rawQuery);
  if (query.length < 2) return [];

  const matches: BrandMatch[] = [];
  for (const brand of brands) {
    const byName = nameConfidence(query, normalizeName(brand.name));
    let best: BrandMatch | null =
      byName > 0 ? { brand, confidence: byName, matchedOn: "name" } : null;

    for (const alias of brand.aliases ?? []) {
      const byAlias = nameConfidence(query, normalizeName(alias));
      if (byAlias > (best?.confidence ?? 0)) {
        best = { brand, confidence: byAlias, matchedOn: "alias" };
      }
    }
    if (best) matches.push(best);
  }
  return matches.sort((a, b) => b.confidence - a.confidence);
}
