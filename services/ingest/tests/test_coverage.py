import polars as pl
import pytest

from discovery import coverage as cov


@pytest.fixture()
def registry(tmp_path):
    brands = tmp_path / "brands"
    brands.mkdir()
    (brands / "pasqually-s-pizza.yaml").write_text(
        'brand: "Pasqually\'s Pizza & Wings"\n'
        'aliases: ["Pasquallys Pizza and Wings"]\n'
        "sources:\n"
        '  - url: "https://example.com"\n'
        '    publication: "Example"\n'
    )
    (brands / "nonexistent.yaml").write_text(
        'brand: "Definitely Not In Any Dataset XYZQ"\nsources: []\n'
    )
    return tmp_path


@pytest.fixture()
def places_parquet(tmp_path):
    df = pl.DataFrame(
        {
            "name_raw": [
                "Pasqually's Pizza and Wings",
                "Joe's Pizza",
                "Cypress Deli Market Corp",
            ],
            "category": ["pizza_restaurant", "pizza_restaurant", "deli"],
        }
    )
    path = tmp_path / "places.parquet"
    df.write_parquet(path)
    return path


def test_hit_via_fuzzy_and_alias(registry, places_parquet):
    report = cov.run(places_parquet, registry_dir=registry)
    by_slug = {r.entry.slug: r for r in report["results"]}
    assert by_slug["pasqually-s-pizza"].hit
    assert not by_slug["nonexistent"].hit
    assert report["total_brands"] == 2
    assert report["hits"] == 1
    assert report["pct"] == 50.0


def test_unsourced_brands_flagged(registry, places_parquet):
    report = cov.run(places_parquet, registry_dir=registry)
    assert report["unsourced_brands"] == ["nonexistent"]


def test_verdict_bands():
    assert cov.verdict(55).startswith("PROCEED")
    assert cov.verdict(35).startswith("MARGINAL")
    assert cov.verdict(10).startswith("STOP")


def _match_one(brand, aliases, place_names):
    import polars as pl

    entries = [cov.BrandEntry(slug="x", brand=brand, aliases=aliases)]
    places = pl.DataFrame(
        {
            "name_raw": place_names,
            "category": ["restaurant"] * len(place_names),
            "name_normalized": [cov.normalize_dba(n) for n in place_names],
        }
    )
    return cov.match_brands(entries, places)[0]


def test_subset_wrong_direction_is_not_a_hit():
    # A place called just "Monster" must NOT count as presence of "Monster Mac".
    r = _match_one("Monster Mac", [], ["Monster", "Totally Unrelated"])
    assert not r.hit


def test_brand_contained_in_place_name_is_a_hit():
    r = _match_one("Nice Day", [], ["Nice Day Chinese"])
    assert r.hit


def test_subset_extra_token_cap():
    r = _match_one("Nice Day", [], ["Have A Nice Day Cafe Lounge"])
    assert not r.hit


def test_leading_the_is_insensitive():
    r = _match_one("The Burger Den", [], ["Burger Den"])
    assert r.hit


def test_near_typo_hits_via_sort_ratio():
    r = _match_one("MrBeast Burger", ["Mr Beast Burger"], ["Mr Beast Burger"])
    assert r.hit


def test_empty_registry_is_fatal(tmp_path, places_parquet):
    (tmp_path / "brands").mkdir()
    with pytest.raises(ValueError):
        cov.run(places_parquet, registry_dir=tmp_path)
