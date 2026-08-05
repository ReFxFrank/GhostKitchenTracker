import polars as pl

from normalize.inspections import (
    SENTINEL_DATE,
    normalize_snapshot,
    pluto_frame,
)


def _row(**kw) -> dict:
    base = {
        "camis": "50000001",
        "dba": "TEST KITCHEN LLC",
        "boro": "Queens",
        "building": "100",
        "street": "MAIN ST",
        "zipcode": "11385",
        "phone": "7185550100",
        "cuisine_description": "Pizza",
        "inspection_date": "2025-03-01T00:00:00.000",
        "action": "Violations were cited in the following area(s).",
        "violation_code": "10F",
        "violation_description": "Non-food contact surface improperly maintained.",
        "critical_flag": "Not Critical",
        "score": "12",
        "grade": "A",
        "grade_date": "2025-03-01T00:00:00.000",
        "record_date": "2026-08-01T00:00:00.000",
        "inspection_type": "Cycle Inspection / Initial Inspection",
        "latitude": "40.7",
        "longitude": "-73.9",
        "bin": "4085660",
        "bbl": "4035520064",
    }
    base.update(kw)
    return base


def test_multi_violation_inspection_dedupes_to_one():
    df = pl.DataFrame(
        [
            _row(violation_code="10F"),
            _row(violation_code="08A", violation_description="Facility not vermin proof."),
            _row(violation_code="06D", critical_flag="Critical"),
        ]
    )
    frames = normalize_snapshot(df)
    assert len(frames["inspections"]) == 1
    assert len(frames["violations"]) == 3
    assert len(frames["establishments"]) == 1


def test_sentinel_rows_keep_establishment_but_no_inspection():
    df = pl.DataFrame(
        [
            _row(
                camis="50000002",
                inspection_date=f"{SENTINEL_DATE}T00:00:00.000",
                violation_code=None,
                violation_description=None,
                action=None,
                score=None,
                grade=None,
                grade_date=None,
            )
        ]
    )
    frames = normalize_snapshot(df)
    est = frames["establishments"]
    assert len(est) == 1
    assert est["never_inspected"][0] is True
    assert est["first_seen"][0] is None
    assert len(frames["inspections"]) == 0
    assert len(frames["violations"]) == 0


def test_violation_text_is_verbatim():
    ugly = "  §81.07 — Mice  droppings   OBSERVED;;    do NOT titlecase me  "
    df = pl.DataFrame([_row(violation_description=ugly)])
    frames = normalize_snapshot(df)
    assert frames["violations"]["description_verbatim"][0] == ugly


def test_establishment_latest_record_wins():
    df = pl.DataFrame(
        [
            _row(dba="OLD NAME INC", record_date="2025-01-01T00:00:00.000"),
            _row(dba="NEW NAME INC", record_date="2026-01-01T00:00:00.000"),
        ]
    )
    frames = normalize_snapshot(df)
    est = frames["establishments"]
    assert est["dba_raw"][0] == "NEW NAME INC"
    assert est["dba_normalized"][0] == "new name"


def test_two_inspections_same_camis_stay_separate():
    df = pl.DataFrame(
        [
            _row(inspection_date="2025-03-01T00:00:00.000"),
            _row(inspection_date="2025-09-15T00:00:00.000", violation_code="04L"),
        ]
    )
    frames = normalize_snapshot(df)
    assert len(frames["inspections"]) == 2


def test_pluto_bbl_decimal_string_parses_to_int():
    df = pl.DataFrame(
        [
            {
                "bbl": "2054800111.00000000",
                "borough": "BX",
                "address": "100 MAIN ST",
                "bldgclass": "A5",
                "landuse": "1",
                "bldgarea": "1683",
                "lotarea": "1700",
                "numfloors": "2.0000000",
                "unitstotal": "1",
                "ownername": "OWNER",
                "yearbuilt": "1950",
                "latitude": "40.8",
                "longitude": "-73.9",
            }
        ]
    )
    out = pluto_frame(df)
    assert out["bbl"][0] == 2054800111
    assert out["bldgarea"][0] == 1683
    assert out["numfloors"][0] == 2.0
