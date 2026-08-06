const STREET_ABBREVIATIONS: Record<string, string> = {
  street: "st",
  avenue: "ave",
  boulevard: "blvd",
  drive: "dr",
  road: "rd",
  lane: "ln",
  court: "ct",
  place: "pl",
  parkway: "pkwy",
  highway: "hwy",
  suite: "ste",
  unit: "ste",
  apartment: "ste",
  apt: "ste",
  north: "n",
  south: "s",
  east: "e",
  west: "w",
};

export function normalizeName(raw: string): string {
  return raw
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/[^a-z0-9 ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Normalize a postal address enough that two hand-typed copies of the same
 * address collide: lowercase, strip punctuation, unify common street-suffix
 * spellings, drop zip+4 tails.
 */
export function normalizeAddress(raw: string): string {
  const tokens = raw
    .replace(/\b(\d{5})-\d{4}\b/g, "$1")
    .toLowerCase()
    .replace(/[^a-z0-9 ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .split(" ")
    .map((t) => STREET_ABBREVIATIONS[t] ?? t);
  return tokens.join(" ");
}

export function tokenize(normalized: string): string[] {
  return normalized.split(" ").filter(Boolean);
}
