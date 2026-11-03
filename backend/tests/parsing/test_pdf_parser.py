from datetime import date
from decimal import Decimal

import pytest

from app.services.parsing.base import ParsedTransaction, StatementParseError
from app.services.parsing.pdf_parser import MAX_PAGES, GenericPdfParser
from tests.parsing.pdf_factory import blank_pdf, table_pdf, text_pdf

parser = GenericPdfParser()
HEADER = ("Tarih", "Aciklama", "Tutar")


def test_can_parse_checks_pdf_signature_not_extension() -> None:
    assert parser.can_parse("ekstre.pdf", b"%PDF-1.7 ...")
    assert not parser.can_parse("ekstre.pdf", b"not a pdf")


def test_parses_ruled_table() -> None:
    content = table_pdf(
        HEADER,
        [("05.10.2026", "MIGROS KADIKOY", "-1.234,56 TL"), ("06.10.2026", "MAAS", "45.000,00")],
    )

    assert parser.parse(content).transactions == [
        ParsedTransaction(date(2026, 10, 5), "MIGROS KADIKOY", Decimal("-1234.56")),
        ParsedTransaction(date(2026, 10, 6), "MAAS", Decimal("45000.00")),
    ]


def test_table_continues_on_pages_without_header() -> None:
    content = table_pdf(
        HEADER,
        [("05.10.2026", "A101", "-85,50")],
        [("07.10.2026", "SHELL", "-1.500,00")],
    )

    descriptions = [t.description for t in parser.parse(content).transactions]
    assert descriptions == ["A101", "SHELL"]


def test_falls_back_to_text_lines_without_table() -> None:
    content = text_pdf(
        [
            "ORNEK BANKA - HESAP EKSTRESI",
            "Donem: 01.10.2026 - 31.10.2026",
            "05.10.2026  NETFLIX.COM  -149,99 TL  10.000,00 TL",
            "06.10.2026  KIRA ODEMESI  -15.000,00",
            "Toplam  -15.149,99",
        ]
    )

    assert parser.parse(content).transactions == [
        ParsedTransaction(date(2026, 10, 5), "NETFLIX.COM", Decimal("-149.99")),
        ParsedTransaction(date(2026, 10, 6), "KIRA ODEMESI", Decimal("-15000.00")),
    ]


# Laid out like a real credit card statement; every name and number is made up.
CARD_STATEMENT = [
    "ORNEK BANK KREDI KARTI EKSTRESI",
    "Kart Limiti : 20.000,00 TL",
    "Hesap Kesim Tarihi : 04/10/2026",
    "Son Odeme Tarihi : 14/10/2026",
    "Asgari Odeme Tutari : 1.500,00 TL",
    "Islem Tarihi Islem Aciklamasi Tutar",
    "07/09/2026 07/09 ORNEK MAGAZA 01.Tak ISTANBUL 1.200,00 TL Islemin 1/3 Taksidi 400,00",
    "10/09/2026 ORNEK MARKET ANKARA 159,90",
    "15/09/2026 ODEME-TESEKKUR ANKARA 5.000,00+",
    "Onceki Bakiye + Harcamalar - Odemeleriniz = Donem Borcu",
]


def test_card_statement_reads_purchases_as_spending_and_payments_as_credit() -> None:
    assert parser.parse(text_pdf(CARD_STATEMENT)).transactions == [
        ParsedTransaction(
            date(2026, 9, 7),
            "07/09 ORNEK MAGAZA 01.Tak ISTANBUL 1.200,00 TL Islemin 1/3 Taksidi",
            Decimal("-400.00"),
        ),
        ParsedTransaction(date(2026, 9, 10), "ORNEK MARKET ANKARA", Decimal("-159.90")),
        ParsedTransaction(date(2026, 9, 15), "ODEME-TESEKKUR ANKARA", Decimal("5000.00")),
    ]


def test_account_statement_keeps_its_signs() -> None:
    # One card-like phrase alone is not enough to flip the signs.
    content = text_pdf(["Hesap Kesim Tarihi : 31.10.2026", "05.10.2026  MAAS  45.000,00"])

    assert parser.parse(content).transactions == [
        ParsedTransaction(date(2026, 10, 5), "MAAS", Decimal("45000.00")),
    ]


def test_identical_copy_of_a_page_is_read_once() -> None:
    content = text_pdf(CARD_STATEMENT, copies=2)

    assert len(parser.parse(content).transactions) == 3


def test_different_pages_with_identical_transactions_are_all_kept() -> None:
    content = table_pdf(
        HEADER,
        [("04.10.2026", "STARBUCKS", "-95,00")],
        [("04.10.2026", "STARBUCKS", "-95,00"), ("05.10.2026", "A101", "-85,50")],
    )

    assert len(parser.parse(content).transactions) == 3


def test_pdf_without_text_reports_scanned_document() -> None:
    with pytest.raises(StatementParseError, match="scanned"):
        parser.parse(blank_pdf())


def test_pdf_with_text_but_no_transactions_raises_error() -> None:
    with pytest.raises(StatementParseError, match="No transactions"):
        parser.parse(text_pdf(["Bu bir ekstre degil."]))


def test_corrupt_pdf_raises_error() -> None:
    with pytest.raises(StatementParseError, match="could not be opened"):
        parser.parse(b"%PDF-1.4\nthis is not really a pdf")


def test_too_many_pages_raises_error() -> None:
    with pytest.raises(StatementParseError, match="pages"):
        parser.parse(blank_pdf(pages=MAX_PAGES + 1))
