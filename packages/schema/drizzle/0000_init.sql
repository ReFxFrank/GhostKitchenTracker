CREATE TYPE "public"."claim_assertion" AS ENUM('confirms', 'denies', 'corrects');--> statement-breakpoint
CREATE TYPE "public"."evidence_family" AS ENUM('TESTIMONY', 'LOCATION', 'ENTITY', 'PHONE', 'MENU', 'MEDIA');--> statement-breakpoint
CREATE TYPE "public"."evidence_kind" AS ENUM('OPERATOR_CLAIM_VERIFIED', 'OPERATOR_PUBLIC_STATEMENT', 'USER_REPORT', 'SHARED_BIN', 'EXACT_ADDRESS_MATCH', 'GEO_PROXIMITY', 'LEGAL_ENTITY_MATCH', 'PHONE_EXACT', 'FINGERPRINT_HIGH', 'FINGERPRINT_MED', 'IMAGE_PHASH_MATCH');--> statement-breakpoint
CREATE TYPE "public"."link_tier" AS ENUM('CONFIRMED', 'LIKELY', 'POSSIBLE', 'SUPPRESSED');--> statement-breakpoint
CREATE TYPE "public"."venue_type" AS ENUM('LIKELY_FACILITY', 'LIKELY_FOODCOURT', 'LIKELY_SINGLE_KITCHEN', 'INSTITUTIONAL', 'UNKNOWN');--> statement-breakpoint
CREATE TABLE "brand_links" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"brand_id" bigint NOT NULL,
	"camis" bigint,
	"bin" integer NOT NULL,
	"score" integer NOT NULL,
	"family_count" integer NOT NULL,
	"has_documentary" boolean NOT NULL,
	"tier" "link_tier" GENERATED ALWAYS AS ((CASE
        WHEN score >= 100 AND has_documentary THEN 'CONFIRMED'
        WHEN score >= 60 AND family_count >= 2 THEN 'LIKELY'
        WHEN score >= 35 THEN 'POSSIBLE'
        ELSE 'SUPPRESSED'
      END)::link_tier) STORED,
	"computed_at" timestamp with time zone DEFAULT now() NOT NULL,
	"superseded_by" bigint
);
--> statement-breakpoint
CREATE TABLE "buildings" (
	"bin" integer PRIMARY KEY NOT NULL,
	"bbl" bigint,
	"lat" double precision,
	"lng" double precision,
	"geom" geometry(point),
	"boro" text,
	"canonical_address" text,
	"bldg_class" text,
	"bldg_class_group" text,
	"bldg_area" bigint,
	"num_floors" real,
	"owner_name" text,
	"year_built" integer,
	"venue_type" "venue_type" DEFAULT 'UNKNOWN' NOT NULL,
	"venue_score" real,
	"venue_classified_at" timestamp with time zone
);
--> statement-breakpoint
CREATE TABLE "candidate_brands" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"gers_id" text NOT NULL,
	"name_normalized" text NOT NULL,
	"bin" integer NOT NULL,
	"discovered_at" timestamp with time zone DEFAULT now() NOT NULL,
	"dismissed" boolean DEFAULT false NOT NULL,
	"dismissed_reason" text
);
--> statement-breakpoint
CREATE TABLE "claims" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"brand_id" bigint NOT NULL,
	"bin" integer,
	"claimant_email" text,
	"verification_method" text,
	"verified_at" timestamp with time zone,
	"assertion" "claim_assertion" NOT NULL,
	"corrected_bin" integer,
	"operator_note" text,
	"published" boolean DEFAULT false NOT NULL
);
--> statement-breakpoint
CREATE TABLE "establishments" (
	"camis" bigint PRIMARY KEY NOT NULL,
	"bin" integer,
	"dba_raw" text,
	"dba_normalized" text,
	"phone_normalized" text,
	"cuisine" text,
	"first_seen" date,
	"last_seen" date,
	"status" text
);
--> statement-breakpoint
CREATE TABLE "evidence" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"brand_link_id" bigint NOT NULL,
	"family" "evidence_family" NOT NULL,
	"kind" "evidence_kind" NOT NULL,
	"weight" integer NOT NULL,
	"payload_json" jsonb,
	"source_name" text NOT NULL,
	"source_url" text,
	"retrieved_at" timestamp with time zone NOT NULL
);
--> statement-breakpoint
CREATE TABLE "inspections" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"camis" bigint NOT NULL,
	"inspected_at" date NOT NULL,
	"action" text,
	"score" integer,
	"grade" text,
	"graded_at" date,
	"type" text
);
--> statement-breakpoint
CREATE TABLE "places" (
	"gers_id" text PRIMARY KEY NOT NULL,
	"name_raw" text NOT NULL,
	"name_normalized" text,
	"category" text,
	"confidence" real,
	"operating_status" text,
	"phone_normalized" text,
	"website" text,
	"lat" double precision,
	"lng" double precision,
	"geom" geometry(point),
	"bin" integer,
	"source_license" text NOT NULL,
	"source_release" text NOT NULL,
	"ingested_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "reports" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"brand_id" bigint,
	"bin" integer,
	"submitter_note" text NOT NULL,
	"submitted_at" timestamp with time zone DEFAULT now() NOT NULL,
	"status" text DEFAULT 'pending' NOT NULL,
	"reviewed_at" timestamp with time zone
);
--> statement-breakpoint
CREATE TABLE "takedowns" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"subject_type" text NOT NULL,
	"subject_id" text NOT NULL,
	"claim" text NOT NULL,
	"received_at" timestamp with time zone DEFAULT now() NOT NULL,
	"resolved_at" timestamp with time zone,
	"outcome" text
);
--> statement-breakpoint
CREATE TABLE "violations" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"inspection_id" bigint NOT NULL,
	"code" text,
	"description_verbatim" text NOT NULL,
	"critical_flag" text
);
--> statement-breakpoint
CREATE TABLE "virtual_brands" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"name_normalized" text NOT NULL,
	"first_observed" date,
	"source_note" text,
	"promoted_from_candidate" bigint
);
--> statement-breakpoint
ALTER TABLE "brand_links" ADD CONSTRAINT "brand_links_brand_id_virtual_brands_id_fk" FOREIGN KEY ("brand_id") REFERENCES "public"."virtual_brands"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "brand_links" ADD CONSTRAINT "brand_links_camis_establishments_camis_fk" FOREIGN KEY ("camis") REFERENCES "public"."establishments"("camis") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "brand_links" ADD CONSTRAINT "brand_links_bin_buildings_bin_fk" FOREIGN KEY ("bin") REFERENCES "public"."buildings"("bin") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "candidate_brands" ADD CONSTRAINT "candidate_brands_gers_id_places_gers_id_fk" FOREIGN KEY ("gers_id") REFERENCES "public"."places"("gers_id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "candidate_brands" ADD CONSTRAINT "candidate_brands_bin_buildings_bin_fk" FOREIGN KEY ("bin") REFERENCES "public"."buildings"("bin") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claims" ADD CONSTRAINT "claims_brand_id_virtual_brands_id_fk" FOREIGN KEY ("brand_id") REFERENCES "public"."virtual_brands"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claims" ADD CONSTRAINT "claims_bin_buildings_bin_fk" FOREIGN KEY ("bin") REFERENCES "public"."buildings"("bin") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "establishments" ADD CONSTRAINT "establishments_bin_buildings_bin_fk" FOREIGN KEY ("bin") REFERENCES "public"."buildings"("bin") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "evidence" ADD CONSTRAINT "evidence_brand_link_id_brand_links_id_fk" FOREIGN KEY ("brand_link_id") REFERENCES "public"."brand_links"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "inspections" ADD CONSTRAINT "inspections_camis_establishments_camis_fk" FOREIGN KEY ("camis") REFERENCES "public"."establishments"("camis") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "places" ADD CONSTRAINT "places_bin_buildings_bin_fk" FOREIGN KEY ("bin") REFERENCES "public"."buildings"("bin") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "reports" ADD CONSTRAINT "reports_brand_id_virtual_brands_id_fk" FOREIGN KEY ("brand_id") REFERENCES "public"."virtual_brands"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "violations" ADD CONSTRAINT "violations_inspection_id_inspections_id_fk" FOREIGN KEY ("inspection_id") REFERENCES "public"."inspections"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "virtual_brands" ADD CONSTRAINT "virtual_brands_promoted_from_candidate_candidate_brands_id_fk" FOREIGN KEY ("promoted_from_candidate") REFERENCES "public"."candidate_brands"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "brand_links_brand_idx" ON "brand_links" USING btree ("brand_id");--> statement-breakpoint
CREATE INDEX "brand_links_bin_idx" ON "brand_links" USING btree ("bin");--> statement-breakpoint
CREATE INDEX "candidate_brands_bin_idx" ON "candidate_brands" USING btree ("bin");--> statement-breakpoint
CREATE INDEX "establishments_bin_idx" ON "establishments" USING btree ("bin");--> statement-breakpoint
CREATE INDEX "evidence_brand_link_idx" ON "evidence" USING btree ("brand_link_id");--> statement-breakpoint
CREATE INDEX "inspections_camis_idx" ON "inspections" USING btree ("camis");--> statement-breakpoint
CREATE INDEX "places_bin_idx" ON "places" USING btree ("bin");--> statement-breakpoint
CREATE INDEX "violations_inspection_idx" ON "violations" USING btree ("inspection_id");