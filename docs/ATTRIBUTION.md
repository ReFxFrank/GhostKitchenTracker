# Attribution

_Attribution is not optional. This document records every obligation the
project carries, and the public attribution page is **generated from actual
data** (`places.source_license` is NOT NULL per record) — not hand-written and
left to rot. Rendered as a public page from Phase 4 onward. Last revised:
2026-08-05._

## Overture Maps Foundation — Places theme

The `places` table is built from the Overture Maps **places** theme, pinned
release **2026-07-22.0** (see `SOURCES.md`).

- Records are licensed **CDLA Permissive 2.0** or **Apache 2.0** depending on
  the per-record source. Both permit commercial use and durable storage; both
  require attribution. Each ingested record stores its license in
  `places.source_license`, so the public attribution page can state exactly
  which licenses cover the data actually in use, with counts.
- Required notice, displayed on the attribution page and in the site footer's
  attribution link:

  > Place data © Overture Maps Foundation and contributors, from the Overture
  > Maps places theme (release 2026-07-22.0), available under the CDLA
  > Permissive 2.0 and Apache 2.0 licenses. Sources include Meta, Microsoft,
  > Foursquare, and PinMeTo.

- License texts: CDLA Permissive 2.0
  (https://cdla.dev/permissive-2-0/), Apache 2.0
  (https://www.apache.org/licenses/LICENSE-2.0).

## Foursquare OS Places (contingent)

Pulled **only if** the Phase 1 coverage gate lands in the 30–50% band and a
supplement is needed. Licensed **Apache 2.0**. If ingested, records carry
`source_license = 'Apache-2.0'` and the attribution page adds:

> Includes Foursquare OS Places data, © Foursquare Labs, Inc., available under
> the Apache 2.0 license.

## OpenStreetMap — basemap only

The map basemap is rendered from a self-hosted PMTiles archive derived from
OpenStreetMap via Protomaps.

- **ODbL** applies. Required notice on every map view: **© OpenStreetMap
  contributors** (linked to https://www.openstreetmap.org/copyright), plus
  **© Protomaps** for the tile build.
- **Hard boundary (license firewall):** OSM data is used for *display only*.
  No OSM POI record is ever joined, conflated, or imported into the `places`
  table or any analytical table. Rendering a basemap under our markers is not
  a database join; POI conflation would be, and could pull the project's
  derivative database under ODbL share-alike terms. This boundary is a §10
  guardrail — violating it is a defect, not a style note.

## NYC Open Data

DOHMH Restaurant Inspection Results, PLUTO, and DCWP Issued Licenses are
published through the NYC Open Data portal, which provides data free for use
without restriction, with the request that data be attributed to the source
agency and not be presented as official city communication.

Attribution line, displayed on the attribution page:

> Contains public data from NYC Open Data: NYC Department of Health and Mental
> Hygiene (restaurant inspection results), NYC Department of City Planning
> (PLUTO), and NYC Department of Consumer and Worker Protection (issued
> licenses). This site is not affiliated with or endorsed by the City of New
> York. Data reflects the dated snapshots recorded in SOURCES.md, not
> necessarily the city's current records.

Every violation rendered on the site links back to the establishment's official
DOHMH record (by CAMIS), so the city's live record is always one click away
from our snapshot of it.

## Generated, not hand-maintained

The public attribution page is produced from:

1. `places.source_license` — per-record license, aggregated to counts per
   license at render time.
2. `places.source_release` — the pinned Overture release(s) actually present
   in the data.
3. The static notices above for OSM/Protomaps and NYC Open Data.

If a new source is ever added without a license recorded per row, ingest fails
loudly. That is by design.
