"""PLUTO (Socrata 64uk-42ks) — building/lot attributes for the venue classifier.

We $select only the fields the classifier needs; the full dataset is ~860k lots
with 90+ columns. Field list verified against the live catalog 2026-08-05.
"""

from __future__ import annotations

import config
from snapshots import Snapshot
from sources import socrata

SOURCE = "pluto"

SELECT_FIELDS = [
    "bbl", "borough", "address", "bldgclass", "landuse", "bldgarea", "lotarea",
    "numfloors", "unitstotal", "ownername", "yearbuilt", "latitude", "longitude",
]

EXPECTED_FIELDS = set(SELECT_FIELDS)


def fetch(
    page_size: int = socrata.DEFAULT_PAGE_SIZE,
    max_pages: int | None = None,
    snapshot: Snapshot | None = None,
) -> Snapshot:
    return socrata.fetch_to_snapshot(
        dataset_id=config.PLUTO_DATASET,
        source_name=SOURCE,
        expected_fields=EXPECTED_FIELDS,
        select=SELECT_FIELDS,
        page_size=page_size,
        max_pages=max_pages,
        snapshot=snapshot,
    )
