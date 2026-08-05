"""Central configuration. NYC-specific by design — do not parameterize the jurisdiction."""

from __future__ import annotations

import os
from pathlib import Path

# Repo layout: services/ingest/config.py → repo root is two levels up.
_REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = Path(os.environ.get("SEANCE_DATA_DIR", _REPO_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"  # derived parquet, gitignored; raw/ stays immutable

# The registry is version-controlled truth (git history = audit log). It stays
# in the repo even when SEANCE_DATA_DIR points raw/staging somewhere else.
REGISTRY_DIR = Path(os.environ.get("SEANCE_REGISTRY_DIR", _REPO_ROOT / "data" / "registry"))

SOCRATA_BASE = "https://data.cityofnewyork.us"
SOCRATA_APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN") or None

# Dataset IDs verified against live catalogs 2026-08-05 — see docs/SOURCES.md.
DOHMH_DATASET = "43nn-pn8j"
PLUTO_DATASET = "64uk-42ks"
DCWP_DATASET = "w7w3-xahh"

# Pinned Overture release — verified on S3 2026-08-05. Changing this pin is a
# deliberate, logged act (update docs/SOURCES.md in the same commit).
OVERTURE_RELEASE = "2026-07-22.0"
OVERTURE_S3 = (
    f"s3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/theme=places/type=place/*"
)

# Foursquare OS Places — contingent supplement, activated by the MARGINAL
# coverage band on 2026-08-05. Gated distribution: needs HF_TOKEN (see
# sources/fsq.py). Pinned like Overture; change deliberately.
FSQ_RELEASE = "2026-07-09"

# Five boroughs bounding box (brief §4).
NYC_BBOX = {"xmin": -74.26, "xmax": -73.68, "ymin": 40.48, "ymax": 40.92}

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgres://seance:seance-dev-only@localhost:5432/seance"
)

# Drizzle migration + invariants, applied by `cli.py init-db`.
SCHEMA_SQL = _REPO_ROOT / "packages" / "schema" / "drizzle" / "0000_init.sql"
INVARIANTS_SQL = _REPO_ROOT / "packages" / "schema" / "sql" / "invariants.sql"
