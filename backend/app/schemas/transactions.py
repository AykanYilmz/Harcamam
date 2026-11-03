import uuid
from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import TransactionType
from app.schemas.categories import RuleRead

MAX_BULK_UPDATE = 500
MAX_PAGE_SIZE = 100


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    statement_id: uuid.UUID
    date: date
    description: str
    # Serialized as a string ("1234.50") so no precision is lost in JSON.
    amount: Decimal
    type: TransactionType
    category_id: uuid.UUID
    is_manually_categorized: bool


class TransactionCategoryUpdate(BaseModel):
    category_id: uuid.UUID
    # When given, also save "descriptions containing this keyword -> category_id" as a rule.
    rule_keyword: str | None = Field(default=None, min_length=1, max_length=100)


class TransactionCorrectionResult(BaseModel):
    transaction: TransactionRead
    rule: RuleRead | None
    # Other transactions re-categorized by the new rule.
    updated_transactions: int


class BulkCategoryUpdate(BaseModel):
    transaction_ids: list[uuid.UUID] = Field(min_length=1, max_length=MAX_BULK_UPDATE)
    category_id: uuid.UUID


class BulkCategoryResult(BaseModel):
    updated: int


class TransactionSort(StrEnum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    AMOUNT_DESC = "amount_desc"
    AMOUNT_ASC = "amount_asc"


class TransactionFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=MAX_PAGE_SIZE)
    date_from: date | None = None
    date_to: date | None = None
    category_id: list[uuid.UUID] = Field(default_factory=list)
    type: TransactionType | None = None
    q: str | None = Field(default=None, min_length=1, max_length=100)
    sort: TransactionSort = TransactionSort.DATE_DESC

    @model_validator(mode="after")
    def check_date_range(self) -> "TransactionFilters":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        return self


class TransactionPage(BaseModel):
    items: list[TransactionRead]
    total: int
    page: int
    page_size: int
    pages: int
