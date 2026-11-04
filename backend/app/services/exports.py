"""Transactions and their summaries as an Excel workbook or a CSV file.

Descriptions come from bank statements, so they are untrusted: written as plain text,
never as something a spreadsheet would run as a formula ("=HYPERLINK(...)").
"""

import csv
import datetime as dt
import io
from dataclasses import dataclass
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.worksheet import Worksheet
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Transaction, TransactionType, User
from app.services.periods import Period
from app.services.reports import monthly_totals, period_calendar, spending_by_category

MONEY_FORMAT = '#,##0.00 "TL"'
DATE_FORMAT = "dd.mm.yyyy"
# A cell starting with one of these may be read as a formula by spreadsheet programs.
FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")
TYPE_LABELS = {TransactionType.INCOME: "Gelir", TransactionType.EXPENSE: "Gider"}


@dataclass(frozen=True)
class ExportRow:
    date: dt.date
    description: str
    category: str
    type: TransactionType
    # Signed: negative for money going out.
    amount: Decimal


def export_rows(db: Session, user: User, start: dt.date, end: dt.date) -> list[ExportRow]:
    rows = db.execute(
        select(Transaction, Category.name)
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == user.id, Transaction.date >= start, Transaction.date <= end)
        .order_by(Transaction.date, Transaction.description)
    )
    return [
        ExportRow(
            date=transaction.date,
            description=transaction.description,
            category=category,
            type=transaction.type,
            amount=(
                transaction.amount
                if transaction.type is TransactionType.INCOME
                else -transaction.amount
            ),
        )
        for transaction, category in rows
    ]


def _write_header(sheet: Worksheet, titles: list[str], widths: list[int]) -> None:
    sheet.append(titles)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for index, width in enumerate(widths):
        sheet.column_dimensions[chr(ord("A") + index)].width = width
    sheet.freeze_panes = "A2"


def _text(sheet: Worksheet, row: int, column: int, value: str) -> None:
    # Assigned as a plain string: openpyxl would otherwise store "=..." as a formula.
    cell = sheet.cell(row=row, column=column)
    cell.value = value
    cell.data_type = "s"


def xlsx(db: Session, user: User, start: dt.date, end: dt.date) -> bytes:
    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "İşlemler"
    _write_header(sheet, ["Tarih", "Açıklama", "Kategori", "Tür", "Tutar"], [12, 50, 16, 8, 16])
    for number, row in enumerate(export_rows(db, user, start, end), start=2):
        sheet.cell(row=number, column=1, value=row.date).number_format = DATE_FORMAT
        _text(sheet, number, 2, row.description)
        _text(sheet, number, 3, row.category)
        _text(sheet, number, 4, TYPE_LABELS[row.type])
        sheet.cell(row=number, column=5, value=row.amount).number_format = MONEY_FORMAT

    periods = period_calendar(user)
    summary = workbook.create_sheet("Aylık özet")
    _write_header(
        summary,
        ["Ay", "Başlangıç", "Bitiş", "Gelir", "Gider", "Elde kalan"],
        [10, 12, 12, 16, 16, 16],
    )
    for totals in monthly_totals(db, user, periods.month_of(start), periods.month_of(end)):
        summary.append(
            [
                f"{totals.month:%Y-%m}",
                totals.period.start,
                totals.period.end,
                totals.income,
                totals.expense,
                totals.net,
            ]
        )
        for cell in summary[summary.max_row][1:3]:
            cell.number_format = DATE_FORMAT
        for cell in summary[summary.max_row][3:]:
            cell.number_format = MONEY_FORMAT

    categories = workbook.create_sheet("Kategoriler")
    _write_header(categories, ["Kategori", "Harcama"], [20, 16])
    spending = spending_by_category(db, user, Period(month=start, start=start, end=end))
    ranked = sorted(spending.items(), key=lambda item: -item[1])
    for number, (category, amount) in enumerate(ranked, start=2):
        # Users name their own categories, so a name is untrusted text too.
        _text(categories, number, 1, category.name)
        categories.cell(row=number, column=2, value=amount).number_format = MONEY_FORMAT

    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def _tr_amount(amount: Decimal) -> str:
    """-1234.5 -> "-1.234,50", as Turkish Excel reads numbers."""
    return f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _safe(text: str) -> str:
    return f"'{text}" if text.startswith(FORMULA_STARTS) else text


def csv_text(db: Session, user: User, start: dt.date, end: dt.date) -> str:
    """Semicolon separated with decimal commas, which Excel in Turkish opens as columns."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Tarih", "Açıklama", "Kategori", "Tür", "Tutar"])
    for row in export_rows(db, user, start, end):
        writer.writerow(
            [
                f"{row.date:%d.%m.%Y}",
                _safe(row.description),
                _safe(row.category),
                TYPE_LABELS[row.type],
                _tr_amount(row.amount),
            ]
        )
    # The byte order mark tells Excel the file is UTF-8, so Turkish letters show correctly.
    return "﻿" + output.getvalue()
