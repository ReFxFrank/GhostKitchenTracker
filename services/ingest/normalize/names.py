"""DBA / business-name canonicalization.

Deterministic, pure, and boring on purpose: the same input always yields the
same output, and no model is involved (brief §10). The goal is that
"Joe's Pizza", "JOES PIZZA, INC." and "Joe's Pizza & Co" all land on the same
canonical string so the name-gap diff compares names, not typography.
"""

from __future__ import annotations

import re
import unicodedata

# Trailing legal-entity tokens, stripped repeatedly ("X PIZZA CORP LLC" → "x pizza").
_LEGAL_SUFFIXES = {
    "llc", "pllc", "inc", "incorporated", "corp", "corporation",
    "co", "company", "ltd", "limited", "llp", "lp",
}

_APOSTROPHES = "'’‘`"


def normalize_dba(raw: str | None) -> str | None:
    if raw is None:
        return None
    s = unicodedata.normalize("NFKD", raw)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # café → cafe
    s = s.casefold()
    for ch in _APOSTROPHES:
        s = s.replace(ch, "")  # joe's → joes (before punctuation spacing)
    s = s.replace(".", "")  # L.L.C. → LLC (before punctuation spacing)
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    tokens = s.split()

    while tokens and tokens[-1] in _LEGAL_SUFFIXES:
        tokens.pop()
    # A dangling conjunction left by suffix-stripping ("blue bottle and co" → "blue bottle and")
    while tokens and tokens[-1] == "and":
        tokens.pop()

    result = " ".join(tokens)
    return result or None
