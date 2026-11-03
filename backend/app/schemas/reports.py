import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

# "2026-10"
MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


class MonthTotalsRead(BaseModel):
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal


class CategorySpendingRead(BaseModel):
    category_id: uuid.UUID
    name: str
    color: str
    icon: str
    amount: Decimal
    # Share of the month's total spending; None when nothing was spent.
    share_pct: float | None
    previous_amount: Decimal
    change_pct: float | None


class MonthlyReportRead(BaseModel):
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal
    transaction_count: int
    previous: MonthTotalsRead
    # None when the previous month is zero (no meaningful percentage).
    income_change_pct: float | None
    expense_change_pct: float | None
    net_change_pct: float | None
    categories: list[CategorySpendingRead]


class TrendReportRead(BaseModel):
    # Oldest first; months without data are included with zeros.
    months: list[MonthTotalsRead]


class MerchantSpendingRead(BaseModel):
    name: str
    amount: Decimal
    transaction_count: int
    category_id: uuid.UUID
    category_name: str


class TopMerchantsRead(BaseModel):
    month: str
    merchants: list[MerchantSpendingRead]


class DaySpendingRead(BaseModel):
    date: date
    amount: Decimal


class DailySpendingRead(BaseModel):
    month: str
    # Every day of the month, in order; days without spending are 0.
    days: list[DaySpendingRead]


class CategoryTrendRead(BaseModel):
    category_id: uuid.UUID
    name: str
    color: str
    icon: str
    # Aligned with CategoryTrendReportRead.months.
    amounts: list[Decimal]
    total: Decimal


class CategoryTrendReportRead(BaseModel):
    months: list[str]
    categories: list[CategoryTrendRead]
