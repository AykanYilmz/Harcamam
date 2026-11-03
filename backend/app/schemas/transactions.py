import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import TransactionType
from app.schemas.categories import RuleRead

MAX_BULK_UPDATE = 500


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
