-- Structural invariants that Postgres enforces and drizzle-kit cannot express.
-- Applied alongside migrations (Phase 1 wires this into the migration flow).
-- These are defects-if-absent, not nice-to-haves — see brief §5 and §10.

-- 1. violations.description_verbatim is WRITE-ONCE and untransformed.
--    Any UPDATE that touches it is an error, full stop.
CREATE OR REPLACE FUNCTION forbid_verbatim_mutation() RETURNS trigger AS $$
BEGIN
  IF NEW.description_verbatim IS DISTINCT FROM OLD.description_verbatim THEN
    RAISE EXCEPTION 'violations.description_verbatim is write-once; it is never transformed';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS violations_verbatim_write_once ON violations;
CREATE TRIGGER violations_verbatim_write_once
  BEFORE UPDATE ON violations
  FOR EACH ROW EXECUTE FUNCTION forbid_verbatim_mutation();

-- 2. brand_links is APPEND-ONLY with supersession. A rescore inserts a new
--    row and sets superseded_by on the old one; nothing else about an
--    existing row may change, and rows are never deleted. The history is the
--    defense record when a displayed link is disputed months later.
CREATE OR REPLACE FUNCTION brand_links_append_only() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'brand_links is append-only; supersede, do not delete';
  END IF;
  IF NEW.brand_id        IS DISTINCT FROM OLD.brand_id
     OR NEW.camis        IS DISTINCT FROM OLD.camis
     OR NEW.bin          IS DISTINCT FROM OLD.bin
     OR NEW.score        IS DISTINCT FROM OLD.score
     OR NEW.family_count IS DISTINCT FROM OLD.family_count
     OR NEW.has_documentary IS DISTINCT FROM OLD.has_documentary
     OR NEW.computed_at  IS DISTINCT FROM OLD.computed_at THEN
    RAISE EXCEPTION 'brand_links rows are immutable except superseded_by; insert a new row instead';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS brand_links_append_only_upd ON brand_links;
CREATE TRIGGER brand_links_append_only_upd
  BEFORE UPDATE ON brand_links
  FOR EACH ROW EXECUTE FUNCTION brand_links_append_only();

DROP TRIGGER IF EXISTS brand_links_append_only_del ON brand_links;
CREATE TRIGGER brand_links_append_only_del
  BEFORE DELETE ON brand_links
  FOR EACH ROW EXECUTE FUNCTION brand_links_append_only();

-- 3. evidence.weight must equal the canonical weight for its kind, and the
--    kind must sit in its declared family. Belt-and-suspenders against a
--    code path inventing precision the methodology doesn't have.
ALTER TABLE evidence DROP CONSTRAINT IF EXISTS evidence_kind_family_weight;
ALTER TABLE evidence ADD CONSTRAINT evidence_kind_family_weight CHECK (
  (kind = 'OPERATOR_CLAIM_VERIFIED'   AND family = 'TESTIMONY' AND weight = 100) OR
  (kind = 'OPERATOR_PUBLIC_STATEMENT' AND family = 'TESTIMONY' AND weight = 100) OR
  (kind = 'USER_REPORT'               AND family = 'TESTIMONY' AND weight = 5)   OR
  (kind = 'SHARED_BIN'                AND family = 'LOCATION'  AND weight = 50)  OR
  (kind = 'EXACT_ADDRESS_MATCH'       AND family = 'LOCATION'  AND weight = 50)  OR
  (kind = 'GEO_PROXIMITY'             AND family = 'LOCATION'  AND weight = 30)  OR
  (kind = 'LEGAL_ENTITY_MATCH'        AND family = 'ENTITY'    AND weight = 45)  OR
  (kind = 'PHONE_EXACT'               AND family = 'PHONE'     AND weight = 40)  OR
  (kind = 'FINGERPRINT_HIGH'          AND family = 'MENU'      AND weight = 40)  OR
  (kind = 'FINGERPRINT_MED'           AND family = 'MENU'      AND weight = 25)  OR
  (kind = 'IMAGE_PHASH_MATCH'         AND family = 'MEDIA'     AND weight = 35)
);
