"""Phone canonicalization: 10 NANP digits or nothing.

DOHMH phone fields contain 9-digit typos, placeholder zeros, and formatting
noise. A phone that can't be reduced to a valid-shaped 10-digit NANP number is
None — the PHONE evidence family must never fire on junk.
"""

from __future__ import annotations

import re


def normalize_phone(raw: str | None) -> str | None:
    if raw is None:
        return None
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return None
    if digits == digits[0] * 10:  # 0000000000, 9999999999 …
        return None
    if digits[0] in "01":  # NANP area codes cannot start with 0 or 1
        return None
    return digits
