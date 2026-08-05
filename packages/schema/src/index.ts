export * from "./schema";

/**
 * Shared types and constants for the linkage engine (brief §9).
 * Weights attach to FAMILIES, not loose evidence rows:
 *   score = Σ over each family of max(weight of evidence present in that family)
 * Double-counting within a family is unrepresentable by construction.
 */

export type EvidenceFamilyName =
  | "TESTIMONY"
  | "LOCATION"
  | "ENTITY"
  | "PHONE"
  | "MENU"
  | "MEDIA";

export type EvidenceKindName =
  | "OPERATOR_CLAIM_VERIFIED"
  | "OPERATOR_PUBLIC_STATEMENT"
  | "USER_REPORT"
  | "SHARED_BIN"
  | "EXACT_ADDRESS_MATCH"
  | "GEO_PROXIMITY"
  | "LEGAL_ENTITY_MATCH"
  | "PHONE_EXACT"
  | "FINGERPRINT_HIGH"
  | "FINGERPRINT_MED"
  | "IMAGE_PHASH_MATCH";

export type LinkTierName = "CONFIRMED" | "LIKELY" | "POSSIBLE" | "SUPPRESSED";

/** Family membership and weight per evidence kind. Closed by type. */
export const EVIDENCE_WEIGHTS: Record<
  EvidenceKindName,
  { family: EvidenceFamilyName; weight: number }
> = {
  OPERATOR_CLAIM_VERIFIED: { family: "TESTIMONY", weight: 100 },
  OPERATOR_PUBLIC_STATEMENT: { family: "TESTIMONY", weight: 100 },
  USER_REPORT: { family: "TESTIMONY", weight: 5 },
  SHARED_BIN: { family: "LOCATION", weight: 50 },
  EXACT_ADDRESS_MATCH: { family: "LOCATION", weight: 50 },
  GEO_PROXIMITY: { family: "LOCATION", weight: 30 },
  LEGAL_ENTITY_MATCH: { family: "ENTITY", weight: 45 },
  PHONE_EXACT: { family: "PHONE", weight: 40 },
  FINGERPRINT_HIGH: { family: "MENU", weight: 40 },
  FINGERPRINT_MED: { family: "MENU", weight: 25 },
  IMAGE_PHASH_MATCH: { family: "MEDIA", weight: 35 },
};

/** Evidence kinds whose presence makes a link "documentary" (tier gate for CONFIRMED). */
export const DOCUMENTARY_KINDS: readonly EvidenceKindName[] = [
  "OPERATOR_CLAIM_VERIFIED",
  "OPERATOR_PUBLIC_STATEMENT",
  "LEGAL_ENTITY_MATCH",
  "SHARED_BIN",
] as const;
