import pytest

from sources.socrata import SchemaDriftError, assert_no_drift


def test_no_drift_passes():
    assert_no_drift("x-x", {"a", "b"}, {"a", "b", "c"})


def test_missing_column_is_fatal():
    with pytest.raises(SchemaDriftError) as exc:
        assert_no_drift("43nn-pn8j", {"camis", "dba", "bin"}, {"camis", "dba"})
    assert "bin" in str(exc.value)


def test_renamed_column_is_fatal():
    with pytest.raises(SchemaDriftError):
        assert_no_drift("x-x", {"violation_description"}, {"violation_desc"})
