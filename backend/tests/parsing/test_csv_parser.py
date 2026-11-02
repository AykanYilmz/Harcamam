from datetime import date
from decimal import Decimal

import pytest

from app.services.parsing.base import ParsedTransaction, StatementParseError
from app.services.parsing.csv_parser import CsvParser

parser = CsvParser()


def parse(text: str, encoding: str = "utf-8") -> list[ParsedTransaction]:
    return parser.parse(text.encode(encoding)).transactions


def test_parses_semicolon_csv_with_signed_amounts() -> None:
    transactions = parse(
        "Tarih;Açıklama;Tutar\n"
        "05.09.2026;MIGROS KADIKOY;-1.234,56 TL\n"
        "06.09.2026;MAAS ODEMESI;45.000,00 TL\n"
    )

    assert transactions == [
        ParsedTransaction(date(2026, 9, 5), "MIGROS KADIKOY", Decimal("-1234.56")),
        ParsedTransaction(date(2026, 9, 6), "MAAS ODEMESI", Decimal("45000.00")),
    ]


def test_parses_comma_csv_with_quoted_amounts() -> None:
    transactions = parse('Date,Description,Amount\n2026-09-05,NETFLIX,"-149,99"\n')

    assert transactions == [ParsedTransaction(date(2026, 9, 5), "NETFLIX", Decimal("-149.99"))]


def test_finds_header_below_account_details() -> None:
    transactions = parse(
        "Hesap Hareketleri\n"
        "Müşteri;ÖRNEK MÜŞTERİ\n"
        "\n"
        "İşlem Tarihi;İşlem Açıklaması;İşlem Tutarı;Bakiye\n"
        "05.09.2026;A101;-85,50;1.000,00\n"
    )

    assert transactions == [ParsedTransaction(date(2026, 9, 5), "A101", Decimal("-85.50"))]


def test_parses_debit_and_credit_columns_in_cp1254() -> None:
    transactions = parse(
        "TARİH;AÇIKLAMA;BORÇ;ALACAK\n05.10.2026;ŞOK MARKET;250,00;\n06.10.2026;İADE;;99,90\n",
        encoding="cp1254",
    )

    assert transactions == [
        ParsedTransaction(date(2026, 10, 5), "ŞOK MARKET", Decimal("-250.00")),
        ParsedTransaction(date(2026, 10, 6), "İADE", Decimal("99.90")),
    ]


def test_handles_utf8_bom() -> None:
    transactions = parse("﻿Tarih;Açıklama;Tutar\n05.09.2026;BIM;-12,00\n")

    assert len(transactions) == 1


def test_skips_rows_that_are_not_transactions() -> None:
    transactions = parse(
        "Tarih;Açıklama;Tutar\n"
        ";Devreden Bakiye;5.000,00\n"
        "05.09.2026;OPET;-900,00\n"
        "\n"
        "Toplam;;-900,00\n"
    )

    assert [t.description for t in transactions] == ["OPET"]


def test_missing_columns_raise_error() -> None:
    with pytest.raises(StatementParseError, match="columns"):
        parse("Ad;Soyad\nAli;Veli\n")


def test_unreadable_amount_reports_row_number() -> None:
    with pytest.raises(StatementParseError, match="Row 3"):
        parse("Tarih;Açıklama;Tutar\n05.09.2026;BIM;-12,00\n06.09.2026;A101;on iki lira\n")


def test_header_without_transactions_raises_error() -> None:
    with pytest.raises(StatementParseError, match="No transactions"):
        parse("Tarih;Açıklama;Tutar\n")


def test_binary_content_raises_error() -> None:
    with pytest.raises(StatementParseError):
        parser.parse(b"\x00\x01\x02binary")
