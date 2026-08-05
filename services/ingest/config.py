"""Central configuration. NYC-specific by design — do not parameterize the jurisdiction.

Path resolution works in two layouts:
- Repo checkout: services/ingest/config.py two levels under the repo root.
- Docker image: this file sits at /app with no repo around it; every path the
  container needs comes from env (SEANCE_DATA_DIR, SEANCE_REGISTRY_DIR,
  SEANCE_SCHEMA_DIR — see ops/docker-compose.yml).
"""

from __future__ import annotations

import os
from pathlib import Path


def _find_repo_root() -> Path | None:
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / "packages" / "schema").is_dir() or (ancestor / ".git").exists():
            return ancestor
    return None


_REPO_ROOT = _find_repo_root()

DATA_DIR = Path(
    os.environ.get("SEANCE_DATA_DIR")
    or (_REPO_ROOT / "data" if _REPO_ROOT else Path("/data"))
)
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"  # derived parquet, gitignored; raw/ stays immutable

# The registry is version-controlled truth (git history = audit log). In a repo
# checkout it stays in the repo even when SEANCE_DATA_DIR points raw/staging
# elsewhere; in the container it arrives via the ../data mount.
REGISTRY_DIR = Path(
    os.environ.get("SEANCE_REGISTRY_DIR")
    or (_REPO_ROOT / "data" / "registry" if _REPO_ROOT else DATA_DIR / "registry")
)

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

# DOHMH/DOB placeholder "million BINs": boro-code * 1,000,000 means "no
# specific building identified". Treating these as real BINs would collapse
# thousands of unrelated establishments into five fake mega-buildings and
# poison the SHARED_BIN evidence family. Always null them at normalize time.
PLACEHOLDER_BINS = {1000000, 2000000, 3000000, 4000000, 5000000}

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgres://seance:seance-dev-only@localhost:5432/seance"
)

# Drizzle migration + invariants, applied by `cli.py init-db`. In the container
# these come from the SEANCE_SCHEMA_DIR mount (see ops/docker-compose.yml).
_SCHEMA_DIR = Path(
    os.environ.get("SEANCE_SCHEMA_DIR")
    or (_REPO_ROOT / "packages" / "schema" if _REPO_ROOT else Path("/schema"))
)
SCHEMA_SQL = _SCHEMA_DIR / "drizzle" / "0000_init.sql"
INVARIANTS_SQL = _SCHEMA_DIR / "sql" / "invariants.sql"
