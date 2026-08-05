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


def test_empty_registry_is_fatal(tmp_path, places_parquet):
    (tmp_path / "brands").mkdir()
    with pytest.raises(ValueError):
        cov.run(places_parquet, registry_dir=tmp_path)
