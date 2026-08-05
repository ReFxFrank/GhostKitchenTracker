/**
 * SEANCE core schema (brief §5).
 *
 * Structural invariants live in the database, not in code review:
 *  - `evidence.family` is NOT NULL and the enum is closed. Every evidence row
 *    belongs to exactly one family; a row outside a family is unrepresentable.
 *  - `brand_links.tier` is a GENERATED column derived from score /
 *    family_count / has_documentary. No code path can write a tier that
 *    disagrees with its score, because no code path can write a tier at all.
 *  - `brand_links` are append-only with supersession; `violations.
 *    description_verbatim` is write-once and untransformed. Both are enforced
 *    by triggers in `sql/invariants.sql`, applied alongside migrations.
 *  - `places.source_license` is NOT NULL — correct attribution must be
 *    generatable per record.
 */
import { sql } from "drizzle-orm";
import {
  bigint,
  bigserial,
  boolean,
  date,
  doublePrecision,
  geometry,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  real,
  text,
  timestamp,
} from "drizzle-orm/pg-core";

// ---------------------------------------------------------------------------
// Closed enums
// ---------------------------------------------------------------------------

export const venueType = pgEnum("venue_type", [
  "LIKELY_FACILITY",
  "LIKELY_FOODCOURT",
  "LIKELY_SINGLE_KITCHEN",
  "INSTITUTIONAL",
  "UNKNOWN",
]);

export const evidenceFamily = pgEnum("evidence_family", [
  "TESTIMONY",
  "LOCATION",
  "ENTITY",
  "PHONE",
  "MENU",
  "MEDIA",
]);

export const evidenceKind = pgEnum("evidence_kind", [
  // TESTIMONY
  "OPERATOR_CLAIM_VERIFIED",
  "OPERATOR_PUBLIC_STATEMENT",
  "USER_REPORT",
  // LOCATION
  "SHARED_BIN",
  "EXACT_ADDRESS_MATCH",
  "GEO_PROXIMITY",
  // ENTITY
  "LEGAL_ENTITY_MATCH",
  // PHONE
  "PHONE_EXACT",
  // MENU
  "FINGERPRINT_HIGH",
  "FINGERPRINT_MED",
  // MEDIA
  "IMAGE_PHASH_MATCH",
]);

export const linkTier = pgEnum("link_tier", [
  "CONFIRMED",
  "LIKELY",
  "POSSIBLE",
  "SUPPRESSED",
]);

export const claimAssertion = pgEnum("claim_assertion", [
  "confirms",
  "denies",
  "corrects",
]);

// ---------------------------------------------------------------------------
// Physical world: buildings (BIN is the atom of the whole system)
// ---------------------------------------------------------------------------

export const buildings = pgTable("buildings", {
  bin: integer("bin").primaryKey(),
  bbl: bigint("bbl", { mode: "number" }),
  lat: doublePrecision("lat"),
  lng: doublePrecision("lng"),
  geom: geometry("geom", { type: "point", mode: "xy", srid: 4326 }),
  boro: text("boro"),
  canonicalAddress: text("canonical_address"),
  bldgClass: text("bldg_class"),
  bldgClassGroup: text("bldg_class_group"),
  bldgArea: bigint("bldg_area", { mode: "number" }),
  numFloors: real("num_floors"),
  ownerName: text("owner_name"),
  yearBuilt: integer("year_built"),
  venueType: venueType("venue_type").default("UNKNOWN").notNull(),
  venueScore: real("venue_score"),
  venueClassifiedAt: timestamp("venue_classified_at", { withTimezone: true }),
});

// ---------------------------------------------------------------------------
// DOHMH: establishments, inspections, violations
// ---------------------------------------------------------------------------

export const establishments = pgTable(
  "establishments",
  {
    camis: bigint("camis", { mode: "number" }).primaryKey(),
    bin: integer("bin").references(() => buildings.bin),
    dbaRaw: text("dba_raw"),
    dbaNormalized: text("dba_normalized"),
    phoneNormalized: text("phone_normalized"),
    cuisine: text("cuisine"),
    firstSeen: date("first_seen"),
    lastSeen: date("last_seen"),
    status: text("status"),
  },
  (t) => [index("establishments_bin_idx").on(t.bin)],
);

export const inspections = pgTable(
  "inspections",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    camis: bigint("camis", { mode: "number" })
      .references(() => establishments.camis)
      .notNull(),
    inspectedAt: date("inspected_at").notNull(),
    action: text("action"),
    score: integer("score"),
    grade: text("grade"),
    gradedAt: date("graded_at"),
    type: text("type"),
  },
  (t) => [index("inspections_camis_idx").on(t.camis)],
);

export const violations = pgTable(
  "violations",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    inspectionId: bigint("inspection_id", { mode: "number" })
      .references(() => inspections.id)
      .notNull(),
    code: text("code"),
    // Write-once. Never trimmed, title-cased, truncated, or rephrased —
    // anywhere in the stack, including the UI. Trigger-enforced.
    descriptionVerbatim: text("description_verbatim").notNull(),
    criticalFlag: text("critical_flag"),
  },
  (t) => [index("violations_inspection_idx").on(t.inspectionId)],
);

// ---------------------------------------------------------------------------
// Overture places — DURABLE (permissive licensing: no TTL)
// ---------------------------------------------------------------------------

export const places = pgTable(
  "places",
  {
    gersId: text("gers_id").primaryKey(),
    nameRaw: text("name_raw").notNull(),
    nameNormalized: text("name_normalized"),
    category: text("category"),
    confidence: real("confidence"),
    operatingStatus: text("operating_status"),
    phoneNormalized: text("phone_normalized"),
    website: text("website"),
    lat: doublePrecision("lat"),
    lng: doublePrecision("lng"),
    geom: geometry("geom", { type: "point", mode: "xy", srid: 4326 }),
    bin: integer("bin").references(() => buildings.bin),
    // NOT NULL: attribution must be generatable per record (CDLA-P-2.0 vs Apache-2.0).
    sourceLicense: text("source_license").notNull(),
    // Pinned Overture release this record came from (e.g. "2026-07-22.0").
    sourceRelease: text("source_release").notNull(),
    ingestedAt: timestamp("ingested_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (t) => [index("places_bin_idx").on(t.bin)],
);

// ---------------------------------------------------------------------------
// Discovery output → curated brands → scored links
// ---------------------------------------------------------------------------

export const candidateBrands = pgTable(
  "candidate_brands",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    gersId: text("gers_id")
      .references(() => places.gersId)
      .notNull(),
    nameNormalized: text("name_normalized").notNull(),
    bin: integer("bin")
      .references(() => buildings.bin)
      .notNull(),
    discoveredAt: timestamp("discovered_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    dismissed: boolean("dismissed").default(false).notNull(),
    dismissedReason: text("dismissed_reason"),
  },
  (t) => [index("candidate_brands_bin_idx").on(t.bin)],
);

export const virtualBrands = pgTable("virtual_brands", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  name: text("name").notNull(),
  nameNormalized: text("name_normalized").notNull(),
  firstObserved: date("first_observed"),
  sourceNote: text("source_note"),
  promotedFromCandidate: bigint("promoted_from_candidate", {
    mode: "number",
  }).references(() => candidateBrands.id),
});

export const brandLinks = pgTable(
  "brand_links",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    brandId: bigint("brand_id", { mode: "number" })
      .references(() => virtualBrands.id)
      .notNull(),
    camis: bigint("camis", { mode: "number" }).references(
      () => establishments.camis,
    ),
    bin: integer("bin")
      .references(() => buildings.bin)
      .notNull(),
    // score = Σ over families of max(weight present in that family).
    // Integer arithmetic only — no decimals, no percentages.
    score: integer("score").notNull(),
    familyCount: integer("family_count").notNull(),
    hasDocumentary: boolean("has_documentary").notNull(),
    // GENERATED — the single source of truth for tiers. Ranges cascade
    // top-down: a ≥100 score without documentary evidence is at best LIKELY.
    tier: linkTier("tier").generatedAlwaysAs(
      sql`(CASE
        WHEN score >= 100 AND has_documentary THEN 'CONFIRMED'
        WHEN score >= 60 AND family_count >= 2 THEN 'LIKELY'
        WHEN score >= 35 THEN 'POSSIBLE'
        ELSE 'SUPPRESSED'
      END)::link_tier`,
    ),
    computedAt: timestamp("computed_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    // Append-only with supersession: a rescore inserts a new row and points
    // the old one here. History survives disputes. Trigger-enforced.
    supersededBy: bigint("superseded_by", { mode: "number" }),
  },
  (t) => [
    index("brand_links_brand_idx").on(t.brandId),
    index("brand_links_bin_idx").on(t.bin),
  ],
);

export const evidence = pgTable(
  "evidence",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    brandLinkId: bigint("brand_link_id", { mode: "number" })
      .references(() => brandLinks.id)
      .notNull(),
    family: evidenceFamily("family").notNull(),
    kind: evidenceKind("kind").notNull(),
    weight: integer("weight").notNull(),
    payloadJson: jsonb("payload_json"),
    sourceName: text("source_name").notNull(),
    sourceUrl: text("source_url"),
    retrievedAt: timestamp("retrieved_at", { withTimezone: true }).notNull(),
  },
  (t) => [index("evidence_brand_link_idx").on(t.brandLinkId)],
);

// ---------------------------------------------------------------------------
// Human loops: claims, reports, takedowns
// ---------------------------------------------------------------------------

export const claims = pgTable("claims", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  brandId: bigint("brand_id", { mode: "number" })
    .references(() => virtualBrands.id)
    .notNull(),
  bin: integer("bin").references(() => buildings.bin),
  claimantEmail: text("claimant_email"),
  verificationMethod: text("verification_method"),
  verifiedAt: timestamp("verified_at", { withTimezone: true }),
  assertion: claimAssertion("assertion").notNull(),
  correctedBin: integer("corrected_bin"),
  operatorNote: text("operator_note"),
  published: boolean("published").default(false).notNull(),
});

export const reports = pgTable("reports", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  brandId: bigint("brand_id", { mode: "number" }).references(
    () => virtualBrands.id,
  ),
  bin: integer("bin"),
  submitterNote: text("submitter_note").notNull(),
  submittedAt: timestamp("submitted_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
  status: text("status").default("pending").notNull(),
  reviewedAt: timestamp("reviewed_at", { withTimezone: true }),
});

export const takedowns = pgTable("takedowns", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  subjectType: text("subject_type").notNull(),
  subjectId: text("subject_id").notNull(),
  claim: text("claim").notNull(),
  receivedAt: timestamp("received_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
  resolvedAt: timestamp("resolved_at", { withTimezone: true }),
  outcome: text("outcome"),
});
