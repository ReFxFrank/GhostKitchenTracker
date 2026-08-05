from sources.overture import validate_schema

# Shape observed live on 2026-08-05 (release 2026-07-22.0), abbreviated.
GOOD = {
    "id": "VARCHAR",
    "geometry": "GEOMETRY('OGC:CRS84')",
    "categories": 'STRUCT("primary" VARCHAR, alternate VARCHAR[])',
    "confidence": "DOUBLE",
    "websites": "VARCHAR[]",
    "socials": "VARCHAR[]",
    "phones": "VARCHAR[]",
    "brand": 'STRUCT(wikidata VARCHAR, "names" STRUCT("primary" VARCHAR))',
    "addresses": "STRUCT(freeform VARCHAR, locality VARCHAR, postcode VARCHAR, region VARCHAR)[]",
    "names": 'STRUCT("primary" VARCHAR, common MAP(VARCHAR, VARCHAR))',
    "sources": "STRUCT(property VARCHAR, dataset VARCHAR, license VARCHAR)[]",
    "operating_status": "VARCHAR",
    "basic_category": "VARCHAR",
    "bbox": "STRUCT(xmin DOUBLE, xmax DOUBLE, ymin DOUBLE, ymax DOUBLE)",
}


def test_live_shape_validates_clean():
    assert validate_schema(GOOD) == []


def test_missing_column_reported():
    bad = {k: v for k, v in GOOD.items() if k != "operating_status"}
    problems = validate_schema(bad)
    assert any("operating_status" in p for p in problems)


def test_renamed_struct_subfield_reported():
    bad = dict(GOOD)
    bad["sources"] = "STRUCT(property VARCHAR, dataset VARCHAR, licence_v2 VARCHAR)[]"
    problems = validate_schema(bad)
    assert any("sources" in p and "license" in p for p in problems)


def test_dropped_bbox_subfield_reported():
    bad = dict(GOOD)
    bad["bbox"] = "STRUCT(xmin DOUBLE, xmax DOUBLE)"
    problems = validate_schema(bad)
    assert any("ymin" in p for p in problems)
