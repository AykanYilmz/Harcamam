import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class SubscriptionRead(BaseModel):
    # Identifies the merchant when dismissing it.
    key: str
    name: str
    category_id: uuid.UUID
    category_name: str
    color: str
    icon: str
    # The latest charge: what it costs now.
    amount: Decimal
    yearly_amount: Decimal
    # The old price when a steady price just changed; otherwise None.
    previous_amount: Decimal | None
    charge_count: int
    first_charge: date
    last_charge: date
    # Expected next charge, for active subscriptions.
    next_charge: date | None
    # False when no charge came for over a month and a half: probably cancelled.
    active: bool


class DismissedSubscriptionRead(BaseModel):
    key: str
    name: str


class SubscriptionReport(BaseModel):
    # Of the active subscriptions.
    monthly_total: Decimal
    yearly_total: Decimal
    subscriptions: list[SubscriptionRead]
    dismissed: list[DismissedSubscriptionRead]


class SubscriptionKey(BaseModel):
    key: str = Field(min_length=1, max_length=200)
