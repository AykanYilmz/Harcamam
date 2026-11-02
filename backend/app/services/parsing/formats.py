"""Helpers for the date, amount and text formats used in Turkish bank statements."""

import re
from datetime import date
from decimal import Decimal

_DATE_DMY = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$")
_DATE_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

_CURRENCY = re.compile(r"(TRY|TL|₺)", re.IGNORECASE)
# Turkish: dot groups thousands, comma separates decimals -> 1.234,56
_AMOUNT_TR = re.compile(r"^\d{1,3}(\.\d{3})*(,\d{1,2})?$|^\d+(,\d{1,2})?$")
# English, accepted only when unambiguous -> 1234.56 or 1,234.56
_AMOUNT_EN = re.compile(r"^\d+\.\d{1,2}$|^\d{1,3}(,\d{3})+\.\d{1,2}$")

_TR_CHARS = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_WHITESPACE = re.compile(r"\s+")


def parse_date(value: str) -> date:
    """Parse `GG.AA.YYYY` (also `/` or `-` separated) or ISO `YYYY-MM-DD`."""
    text = value.strip()
    if match := _DATE_DMY.match(text):
        day, month, year = (int(part) for part in match.groups())
    elif match := _DATE_ISO.match(text):
        year, month, day = (int(part) for part in match.groups())
    else:
        raise ValueError(f"Unrecognized date: {value!r}")
    return date(year, month, day)


def parse_amount(value: str) -> Decimal:
    """Parse a signed amount such as `-1.234,56 TL`, `₺85,00`, `1.234,56-` or `(500,00)`."""
    text = _CURRENCY.sub("", value)
    text = _WHITESPACE.sub("", text)

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative, text = True, text[1:-1]
    if text and text[0] in "+-":
        negative, text = text[0] == "-", text[1:]
    elif text.endswith("-"):
        negative, text = True, text[:-1]

    if _AMOUNT_TR.match(text):
        normalized = text.replace(".", "").replace(",", ".")
    elif _AMOUNT_EN.match(text):
        normalized = text.replace(",", "")
    else:
        raise ValueError(f"Unrecognized amount: {value!r}")

    amount = Decimal(normalized)
    return -amount if negative else amount


def normalize_header(value: str) -> str:
    """Lowercase ASCII form of a column header: `İşlem Tarihi` -> `islem tarihi`.

    Translating Turkish letters before lowercasing avoids the `"I".lower() == "i"` vs `ı` trap.
    """
    ascii_text = value.translate(_TR_CHARS).lower()
    return _NON_ALNUM.sub(" ", ascii_text).strip()


def normalize_description(value: str) -> str:
    """Collapse whitespace so cosmetic differences don't change a transaction's identity."""
    return _WHITESPACE.sub(" ", value).strip()
