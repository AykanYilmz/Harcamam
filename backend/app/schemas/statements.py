import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class StatementRead(BaseModel):
    id: uuid.UUID
    file_name: str
    bank_name: str | None
    period_start: date
    period_end: date
    uploaded_at: datetime
    transaction_count: int
    # Totals as printed on the statement, whatever the categories (a credit card's money
    # out is the period's purchases).
    money_in: Decimal
    money_out: Decimal


class StatementImportResult(BaseModel):
    statement: StatementRead
    imported: int
    skipped_duplicates: int
    # How many of the imported transactions no rule recognized.
    uncategorized: int
