# SEANCE

A public, sourced, auditable map of which delivery-app "restaurants" are actually
cooked in the same physical kitchen. New York City only (v1).

**Status:** Phase 0 complete — scaffold and legal posture. No data has been ingested;
no assertions exist yet.

This project indexes public records. It does not accuse anyone of anything. Every
brand→kitchen link the site will ever display must carry a visible evidence trail of
government records or the operator's own statements, with source names and retrieval
dates. If the evidence cannot be shown, the link is not shown. Read
[docs/METHODOLOGY.md](docs/METHODOLOGY.md) for how links are scored and
[docs/LEGAL.md](docs/LEGAL.md) for what the site asserts and how to dispute a record.

## Layout

```
apps/web/          Next.js 15 (App Router, TS, Tailwind) — the public site
services/ingest/   Python 3.12 — fetch, normalize, classify, link (typer CLI)
packages/schema/   Drizzle schema + shared TS types
data/raw/          Immutable dated source snapshots (gitignored)
data/tiles/        Self-hosted PMTiles basemap (gitignored)
data/registry/     Hand-curated YAML — brands, chains, exclusions (committed; git history = audit log)
docs/              LEGAL, METHODOLOGY, ATTRIBUTION, SOURCES
ops/               docker-compose, cron
```

## Run

```sh
docker compose -f ops/docker-compose.yml up --build
```

Brings up Postgres 16 + PostGIS and the Next.js app on http://localhost:3000.
The ingest service is behind the `tools` profile and is run per-stage:

```sh
docker compose -f ops/docker-compose.yml --profile tools run --rm ingest python cli.py --help
```

Copy `.env.example` to `.env` first if you want non-default credentials or a
Socrata app token (required for real ingest volume in Phase 1).

## Phases

Development proceeds in gated phases (see the build brief). Each phase ends with a
stop; the next phase does not begin in the same session.

- [x] **Phase 0** — scaffold, legal posture, dataset ID verification
- [~] **Phase 1** — ingest + the coverage gate. Done: fetchers (DOHMH/PLUTO/DCWP/
  Overture) live-verified at full scale, normalizers + 40 tests, registry seeded
  with 51 source-verified brands, preliminary coverage **47.1% (MARGINAL band)**
  — see `docs/reports/2026-08-05-coverage-preliminary.md`. Remaining: registry
  human review, `init-db`/`load` first run against Postgres, Geosupport install,
  FSQ supplement (needs `HF_TOKEN` — distribution is gated) + re-measure.
- [ ] **Phase 2** — venue classification + name-gap discovery
- [ ] **Phase 3** — linkage engine
- [ ] **Phase 4** — web app
- [ ] **Phase 5** — human loops: claims and reports
- [ ] **Phase 6** — ship

## Ground rules (short form)

- No assertion without a displayed evidence trail.
- Government records are the spine; open place data is discovery only.
- Health data is reproduced verbatim or not at all. Never summarized, never editorialized.
- The operator's own words outrank our inference. A verified denial removes the link — no adjudication.
- No LLM in the data path. No paid data sources. No scraping delivery platforms — permanently.
- No OSM POI data joined into `places` (basemap display only — ODbL boundary).

Full list: §10 of the build brief; public-facing version in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).
