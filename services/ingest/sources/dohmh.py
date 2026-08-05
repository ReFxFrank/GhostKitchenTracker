"""DOHMH Restaurant Inspection Results (Socrata 43nn-pn8j).

One row per violation citation; deduplication to inspection level happens in
normalize/, not here — snapshots are verbatim.

Field list verified against the live catalog 2026-08-05 (docs/SOURCES.md).
"""

from __future__ import annotations

import config
from snapshots import Snapshot
from sources import socrata

SOURCE = "dohmh"

EXPECTED_FIELDS = {
    "camis", "dba", "boro", "building", "street", "zipcode", "phone",
    "cuisine_description", "inspection_date", "action", "violation_code",
    "violation_description", "critical_flag", "score", "grade", "grade_date",
    "record_date", "inspection_type", "latitude", "longitude",
    "community_board", "council_district", "census_tract", "bin", "bbl", "nta",
}


def fetch(
    page_size: int = socrata.DEFAULT_PAGE_SIZE,
    max_pages: int | None = None,
    snapshot: Snapshot | None = None,
) -> Snapshot:
    return socrata.fetch_to_snapshot(
        dataset_id=config.DOHMH_DATASET,
        source_name=SOURCE,
        expected_fields=EXPECTED_FIELDS,
        page_size=page_size,
        max_pages=max_pages,
        snapshot=snapshot,
    )
