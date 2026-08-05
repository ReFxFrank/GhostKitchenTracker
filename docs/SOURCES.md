# Sources

_Every dataset ID and endpoint below was verified against the live catalog on
**2026-08-05** (Phase 0 requirement). Re-verify at ingest time; do not trust
this file over the live catalog if they disagree — but if they disagree, ingest
must fail loudly, not adapt silently._

## Verified datasets

### 1. DOHMH Restaurant Inspection Results — **VERIFIED 2026-08-05**

- **Dataset ID:** `43nn-pn8j` (NYC Open Data / Socrata)
- **Endpoint:** `https://data.cityofnewyork.us/resource/43nn-pn8j.json`
- **Verification:** live query returned current data; sample row carried
  `record_date: 2026-08-04`, non-null `bin` (`4085660`), `bbl`, coordinates,
  and — usefully — an `inspection_date` of `1900-01-01`, confirming the
  permitted-but-never-inspected convention documented in the brief. Field
  names in the JSON API are lowercase snake_case (`camis`, `dba`, `boro`,
  `building`, `street`, `zipcode`, `phone`, `inspection_date`, `bin`, `bbl`,
  `nta`, …).
- **Granularity warning:** one row per violation citation; deduplicate to
  inspection level (`camis` + `inspection_date`) before anything else.
- **Auth:** register a free Socrata app token (`SOCRATA_APP_TOKEN` in `.env`);
  unauthenticated requests are throttled hard.

### 2. PLUTO — **VERIFIED 2026-08-05**

- **Dataset ID:** `64uk-42ks` (NYC Open Data / Socrata), titled "Primary Land
  Use Tax Lot Output (PLUTO)", attributed to the Department of City Planning.
- **Endpoint:** `https://data.cityofnewyork.us/resource/64uk-42ks.json`
- **Verification:** live query returned all fields the venue classifier needs,
  lowercase in the JSON API: `bbl`, `bldgclass`, `bldgarea`, `lotarea`,
  `landuse`, `numfloors`, `unitstotal`, `ownername`, `yearbuilt`.
- **Note:** this is the Socrata tabular PLUTO, sufficient for attribute joins
  on BBL. MapPLUTO (the geometry-bearing shapefile/FGDB product) is published
  separately by DCP on Bytes of the Big Apple; only needed if lot geometry is
  required for point-in-lot BIN resolution, and DCP has moved that endpoint
  before — verify at ingest time.
- **BBL format warning:** the JSON API returns `bbl` as a decimal string
  (e.g. `"2054800111.00000000"`). Parse to integer deliberately; do not
  string-compare.

### 3. DCWP licenses — **VERIFIED 2026-08-05, title changed**

- **Dataset ID:** `w7w3-xahh` (NYC Open Data / Socrata). The brief called this
  "Legally Operating Businesses"; the dataset is now titled **"Issued
  Licenses"**, attributed to the Department of Consumer and Worker Protection.
  Same dataset, renamed upstream.
- **Endpoint:** `https://data.cityofnewyork.us/resource/w7w3-xahh.json`
- **Verification:** live query returned `license_nbr`, `business_name`,
  `dba_trade_name`, `business_category`, `license_status`, address fields, and
  — critically for the `ENTITY` evidence family — non-null `bin` and `bbl` on
  the sample row.

### 4. Overture Maps — Places theme — **VERIFIED & PINNED 2026-08-05**

- **Pinned release: `2026-07-22.0`** — snapshots must be reproducible;
  "latest" is not a version. Changing this pin is a deliberate, logged act.
- **S3 path:**
  `s3://overturemaps-us-west-2/release/2026-07-22.0/theme=places/type=place/*`
- **Verification:** S3 bucket listing on 2026-08-05 showed available release
  prefixes `2026-06-17.0` and `2026-07-22.0`; the
  `theme=places/type=place/` partition confirmed present under the pinned
  release. Note the bucket retains only recent releases — another reason the
  raw NYC extract is snapshotted locally the day it is pulled.
- **Access pattern:** DuckDB (`spatial` + `httpfs`), NYC bbox pushdown, no
  planet download — see brief §4 for the exact query. Output parquet lands in
  `data/raw/overture/{YYYY-MM-DD}/nyc_places.parquet`.
- **Licensing:** per-record licenses live in the data itself — `sources` is a
  list of structs each carrying a `license` field. Values observed in the wild
  on 2026-08-05: `CDLA-Permissive-2.0`, `Apache-2.0`, and `CC0-1.0`. The
  distinct set per record is carried into `places.source_license`. The places
  theme contains **no OpenStreetMap data**, so this join is clean under the
  ODbL firewall (see `ATTRIBUTION.md`).
- **Live schema verification (2026-08-05, release 2026-07-22.0):** DuckDB
  `DESCRIBE` against S3 confirmed all fields the brief relies on, including
  `operating_status` (values observed: `open`, `permanently_closed`, null) and
  `confidence`. The release also adds `basic_category` and a `taxonomy` struct
  not mentioned in the brief — captured in the extract for future use, not yet
  load-bearing. The ingest asserts required columns via live `DESCRIBE` before
  every extract and fails loudly on drift.

### 5. Foursquare OS Places — contingent, not yet pinned

- Apache 2.0, monthly Parquet releases on S3/Hugging Face. Pulled **only if**
  the Phase 1 coverage gate lands in the 30–50% band. If activated, pin the
  release here with the retrieval date, same rules as Overture.

### 6. NYC Geosupport Desktop Edition — not yet installed

- Address → BIN/BBL normalization, local and unlimited, via
  `python-geosupport`. Free download from DCP. Install is Phase 1 work; record
  the Geosupport release version here when installed (DCP versions it
  quarterly, e.g. `26x`).

## Snapshot discipline

- Every fetch writes a dated, compressed, **immutable** file under
  `data/raw/{source}/{YYYY-MM-DD}/`. Downstream stages read snapshots only.
- Any upstream schema change (column renamed, dropped, retyped) must crash the
  ingest with a named error. No defensive defaults.
- Refresh cadence: weekly by cron (Phase 6). Each refresh is a new snapshot
  directory, never an overwrite.

## Verification log

| Date | Who | What |
|---|---|---|
| 2026-08-05 | Phase 0 session | Verified `43nn-pn8j`, `64uk-42ks`, `w7w3-xahh` live on Socrata; confirmed field presence per §4. Listed Overture S3 releases; pinned `2026-07-22.0`; confirmed places partition exists. Noted DCWP dataset title change. |
