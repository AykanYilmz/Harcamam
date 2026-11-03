import uuid
from datetime import date, datetime

from pydantic import BaseModel


class StatementRead(BaseModel):
    id: uuid.UUID
    file_name: str
    bank_name: str | None
    period_start: date
    period_end: date
    uploaded_at: datetime
    transaction_count: int


class StatementImportResult(BaseModel):
    statement: StatementRead
    imported: int
    skipped_duplicates: int
    # How many of the imported transactions no rule recognized.
    uncategorized: int
