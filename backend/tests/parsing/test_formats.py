from datetime import date
from decimal import Decimal

import pytest

from app.services.parsing.formats import (
    normalize_description,
    normalize_text,
    parse_amount,
    parse_card_amount,
    parse_date,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("05.10.2026", date(2026, 10, 5)),
        ("5.1.2026", date(2026, 1, 5)),
        ("05/10/2026", date(2026, 10, 5)),
        ("05-10-2026", date(2026, 10, 5)),
        (" 31.12.2026 ", date(2026, 12, 31)),
        ("2026-10-05", date(2026, 10, 5)),
    ],
)
def test_parse_date(value: str, expected: date) -> None:
    assert parse_date(value) == expected


@pytest.mark.parametrize("value", ["", "32.01.2026", "05.13.2026", "2026.10.05", "dün"])
def test_parse_date_rejects_invalid(value: str) -> None:
    with pytest.raises(ValueError):
        parse_date(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1.234,56", Decimal("1234.56")),
        ("1.234,56 TL", Decimal("1234.56")),
        ("-1.234,56 TL", Decimal("-1234.56")),
        ("₺85,00", Decimal("85.00")),
        ("+500,00", Decimal("500.00")),
        ("1.234,56-", Decimal("-1234.56")),
        ("1.234,56+", Decimal("1234.56")),
        ("(500,00)", Decimal("-500.00")),
        ("1.250.000,00", Decimal("1250000.00")),
        ("85", Decimal("85")),
        ("1.234", Decimal("1234")),
        ("12,5", Decimal("12.5")),
        ("- 45,90 TRY", Decimal("-45.90")),
        ("1 234,56", Decimal("1234.56")),
        ("1234.56", Decimal("1234.56")),
        ("1,234.56", Decimal("1234.56")),
    ],
)
def test_parse_amount(value: str, expected: Decimal) -> None:
    assert parse_amount(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Unsigned on a card statement: a purchase, so money going out.
        ("402,75", Decimal("-402.75")),
        ("1.208,23 TL", Decimal("-1208.23")),
        # Marked: a payment or a refund.
        ("12.345,67+", Decimal("12345.67")),
        ("+500,00", Decimal("500.00")),
        ("-349,00", Decimal("349.00")),
        ("349,00-", Decimal("349.00")),
    ],
)
def test_parse_card_amount(value: str, expected: Decimal) -> None:
    assert parse_card_amount(value) == expected


@pytest.mark.parametrize("value", ["", "TL", "abc", "1,2,3", "12.34.56", "1.23,45", "--5"])
def test_parse_amount_rejects_invalid(value: str) -> None:
    with pytest.raises(ValueError):
        parse_amount(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("İşlem Tarihi", "islem tarihi"),
        ("AÇIKLAMA", "aciklama"),
        ("Açıklama", "aciklama"),
        ("Tutar (TL)", "tutar tl"),
        ("  Borç / Alacak ", "borc alacak"),
    ],
)
def test_normalize_text(value: str, expected: str) -> None:
    assert normalize_text(value) == expected


def test_normalize_description_collapses_whitespace() -> None:
    assert normalize_description("  MIGROS   KADIKOY\t ISTANBUL ") == "MIGROS KADIKOY ISTANBUL"
