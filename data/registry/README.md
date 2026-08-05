# Registry

Hand-curated YAML, committed to git. There is no admin UI on purpose — **the git
history is the audit log**. Every addition, correction, and removal here is
attributable and dated by the commit that made it.

## Contents

- `brands/` — known virtual brands from published reporting or operator
  statements. One file per brand. Seeding 30–50 of these is **Phase 1** work and
  gates the coverage kill-test. `brands/pasqually-s-pizza.yaml` is the format
  exemplar.
- `chains.yaml` — national chain blocklist for the venue classifier (§7).
  Several distinct chains at one BIN ⇒ food court, classify and stop.
- `exclusions.yaml` — **never link or display.** Takedowns and verified operator
  denials land here. Checked at **render time**, not only at scoring time: a
  takedown must take effect on the next deploy without a re-ingest. A verified
  operator denial ends the matter — we do not adjudicate.

## Brand file format

```yaml
brand: "Display Name"
aliases: ["Alternate Spelling"]
operator: "Parent operator, if disclosed"
disclosure_type: operator_public_statement   # operator_public_statement | press_reported | inferred
sources:
  - url: "https://..."
    publication: "..."
    retrieved: "YYYY-MM-DD"
nationwide: true
```

Every source needs a URL, a publication name, and a retrieval date. A brand file
without a source is not a brand file.
