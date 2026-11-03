"""Recognizes transaction columns in a header row; shared by the CSV and PDF parsers."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from app.services.parsing.base import ParsedTransaction, StatementParseError
from app.services.parsing.formats import (
    normalize_description,
    normalize_text,
    parse_amount,
    parse_date,
)

DATE_HEADERS = {"tarih", "islem tarihi", "date", "transaction date"}
DESCRIPTION_HEADERS = {
    "aciklama",
    "islem aciklamasi",
    "aciklamalar",
    "islem",
    "detay",
    "description",
}
AMOUNT_HEADERS = {"tutar", "tutar tl", "islem tutari", "amount"}
DEBIT_HEADERS = {"borc", "borc tl", "borc tutari", "debit"}
CREDIT_HEADERS = {"alacak", "alacak tl", "alacak tutari", "credit"}


@dataclass(frozen=True)
class ColumnMap:
    date: int
    description: int
    amount: int | None = None
    debit: int | None = None
    credit: int | None = None


def _find(headers: list[str], candidates: set[str]) -> int | None:
    return next((index for index, header in enumerate(headers) if header in candidates), None)


def detect_columns(row: Sequence[str | None]) -> ColumnMap | None:
    """Return the column layout if `row` is a header row, otherwise None."""
    headers = [normalize_text(cell or "") for cell in row]
    date = _find(headers, DATE_HEADERS)
    description = _find(headers, DESCRIPTION_HEADERS)
    amount = _find(headers, AMOUNT_HEADERS)
    debit = _find(headers, DEBIT_HEADERS)
    credit = _find(headers, CREDIT_HEADERS)

    if date is None or description is None:
        return None
    if amount is None and (debit is None or credit is None):
        return None
    return ColumnMap(date, description, amount, debit, credit)


def _cell(row: Sequence[str | None], index: int | None) -> str:
    if index is None or index >= len(row):
        return ""
    return (row[index] or "").strip()


def _amount_or_zero(value: str) -> Decimal:
    return parse_amount(value) if value else Decimal(0)


def row_to_transaction(
    row: Sequence[str | None], columns: ColumnMap, row_label: str
) -> ParsedTransaction | None:
    """Convert a data row, or return None for rows that aren't transactions (totals, notes...)."""
    try:
        date = parse_date(_cell(row, columns.date))
    except ValueError:
        return None

    try:
        if columns.amount is not None:
            amount = parse_amount(_cell(row, columns.amount))
        else:
            # Debit and credit are both written as positive numbers.
            debit = abs(_amount_or_zero(_cell(row, columns.debit)))
            credit = abs(_amount_or_zero(_cell(row, columns.credit)))
            amount = credit - debit
    except ValueError as exc:
        raise StatementParseError(f"{row_label}: could not read the amount") from exc

    description = normalize_description(_cell(row, columns.description))
    if amount == 0 or not description:
        return None
    return ParsedTransaction(date=date, description=description, amount=amount)
