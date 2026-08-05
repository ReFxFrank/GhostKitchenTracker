from normalize.names import normalize_dba


def test_basic_lowercase_and_punctuation():
    assert normalize_dba("Joe's Pizza") == "joes pizza"
    assert normalize_dba("JOES PIZZA, INC.") == "joes pizza"


def test_equivalence_across_typography():
    variants = ["Joe's Pizza", "JOES PIZZA INC", "Joes  Pizza,  L.L.C.", "joe's pizza corp."]
    assert len({normalize_dba(v) for v in variants}) == 1


def test_ampersand_becomes_and():
    assert normalize_dba("Pasqually's Pizza & Wings") == "pasquallys pizza and wings"
    assert normalize_dba("Pasquallys Pizza and Wings") == "pasquallys pizza and wings"


def test_real_dohmh_row():
    assert normalize_dba("CYPRESS DELI MARKET CORP.") == "cypress deli market"


def test_stacked_suffixes():
    assert normalize_dba("HALAL FOOD CORP LLC") == "halal food"


def test_dangling_and_after_suffix_strip():
    assert normalize_dba("Blue Bottle & Co") == "blue bottle"


def test_accents_fold():
    assert normalize_dba("Café Añejo") == "cafe anejo"


def test_curly_apostrophe():
    assert normalize_dba("Joe’s Pizza") == "joes pizza"


def test_none_and_empty():
    assert normalize_dba(None) is None
    assert normalize_dba("") is None
    assert normalize_dba("  LLC ") is None  # suffix-only collapses to nothing


def test_numbers_survive():
    assert normalize_dba("Kitchen 21") == "kitchen 21"


def test_suffix_word_in_middle_survives():
    # "co" only strips when trailing.
    assert normalize_dba("Co Op Cafe") == "co op cafe"
