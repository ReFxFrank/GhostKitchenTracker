"""DCWP Issued Licenses (Socrata w7w3-xahh) — legal entity / DBA corroboration
for the ENTITY evidence family (Phase 3 consumes this; Phase 1 just snapshots).

The dataset was retitled upstream from "Legally Operating Businesses" to
"Issued Licenses" — same dataset ID. Verified 2026-08-05 (docs/SOURCES.md).
"""

from __future__ import annotations

import config
from snapshots import Snapshot
from sources import socrata

SOURCE = "dcwp"

EXPECTED_FIELDS = {
    "license_nbr", "business_name", "dba_trade_name", "business_unique_id",
    "business_category", "license_type", "license_status",
    "license_creation_date", "lic_expir_dd", "contact_phone",
    "address_building", "address_street_name", "address_city", "address_state",
    "address_zip", "address_borough", "bin", "bbl", "nta",
    "latitude", "longitude",
}


def fetch(
    page_size: int = socrata.DEFAULT_PAGE_SIZE,
    max_pages: int | None = None,
    snapshot: Snapshot | None = None,
) -> Snapshot:
    return socrata.fetch_to_snapshot(
        dataset_id=config.DCWP_DATASET,
        source_name=SOURCE,
        expected_fields=EXPECTED_FIELDS,
        page_size=page_size,
        max_pages=max_pages,
        snapshot=snapshot,
    )
