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
