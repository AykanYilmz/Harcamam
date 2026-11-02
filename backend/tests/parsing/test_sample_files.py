"""End-to-end parser checks against the fake statements in sample_data/."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.services.parsing.base import ParsedStatement, ParsedTransaction
from app.services.parsing.csv_parser import CsvParser
from app.services.parsing.pdf_parser import GenericPdfParser
from app.services.parsing.registry import get_parser

SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_data"


def parse_sample(file_name: str) -> ParsedStatement:
    content = (SAMPLE_DIR / file_name).read_bytes()
    parser = get_parser(file_name, content)
    assert parser is not None
    return parser.parse(content)


def totals(statement: ParsedStatement) -> tuple[Decimal, Decimal]:
    amounts = [t.amount for t in statement.transactions]
    return sum(a for a in amounts if a > 0), sum(a for a in amounts if a < 0)


@pytest.mark.parametrize(
    ("file_name", "parser_type"),
    [
        ("ornek_hesap_ekstresi_2026_09.csv", CsvParser),
        ("ornek_kredi_karti_2026_10.csv", CsvParser),
        ("ornek_hesap_ekstresi_2026_10.pdf", GenericPdfParser),
    ],
)
def test_registry_picks_parser_for_sample(file_name: str, parser_type: type) -> None:
    content = (SAMPLE_DIR / file_name).read_bytes()

    assert isinstance(get_parser(file_name, content), parser_type)


def test_account_csv() -> None:
    statement = parse_sample("ornek_hesap_ekstresi_2026_09.csv")

    assert len(statement.transactions) == 26
    assert totals(statement) == (Decimal("45087.35"), Decimal("-29160.72"))
    assert statement.transactions[0] == ParsedTransaction(
        date(2026, 9, 1), "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.", Decimal("45000.00")
    )


def test_account_csv_keeps_identical_same_day_purchases() -> None:
    statement = parse_sample("ornek_hesap_ekstresi_2026_09.csv")

    coffees = [t for t in statement.transactions if t.description == "STARBUCKS MODA"]
    assert len(coffees) == 2


def test_credit_card_csv_in_cp1254_with_debit_credit_columns() -> None:
    statement = parse_sample("ornek_kredi_karti_2026_10.csv")

    assert len(statement.transactions) == 13
    assert totals(statement) == (Decimal("5349.00"), Decimal("-10433.28"))
    assert (
        ParsedTransaction(date(2026, 10, 20), "TRENDYOL İADE", Decimal("349.00"))
        in statement.transactions
    )


def test_account_pdf_spans_two_pages() -> None:
    statement = parse_sample("ornek_hesap_ekstresi_2026_10.pdf")

    assert len(statement.transactions) == 27
    assert totals(statement) == (Decimal("46679.45"), Decimal("-29657.37"))
    assert statement.transactions[0].date == date(2026, 9, 26)
    assert statement.transactions[-1] == ParsedTransaction(
        date(2026, 10, 31), "FAİZ GELİRİ", Decimal("92.10")
    )


def test_pdf_and_csv_produce_identical_overlapping_transactions() -> None:
    september = parse_sample("ornek_hesap_ekstresi_2026_09.csv").transactions
    october = parse_sample("ornek_hesap_ekstresi_2026_10.pdf").transactions

    assert september[-5:] == october[:5]
