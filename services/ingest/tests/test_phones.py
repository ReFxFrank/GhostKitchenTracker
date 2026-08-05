from normalize.phones import normalize_phone


def test_formatting_stripped():
    assert normalize_phone("(212) 555-0134") == "2125550134"


def test_leading_one_stripped():
    assert normalize_phone("+1 212 555 0134") == "2125550134"
    assert normalize_phone("12125550134") == "2125550134"


def test_nine_digit_junk_rejected():
    # Real value observed in DOHMH: "929204965"
    assert normalize_phone("929204965") is None


def test_repeated_digit_placeholder_rejected():
    assert normalize_phone("0000000000") is None
    assert normalize_phone("9999999999") is None


def test_invalid_area_code_rejected():
    assert normalize_phone("0125550134") is None
    assert normalize_phone("1125550134") is None


def test_none_and_empty():
    assert normalize_phone(None) is None
    assert normalize_phone("") is None
    assert normalize_phone("N/A") is None
