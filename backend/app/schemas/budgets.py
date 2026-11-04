import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from app.services.budgets import BudgetStatus

# Positive, at most 10 digits before the decimal point (Numeric(12, 2)).
MonthlyLimit = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


class BudgetCreate(BaseModel):
    category_id: uuid.UUID
    monthly_limit: MonthlyLimit


class BudgetCreated(BaseModel):
    id: uuid.UUID


class BudgetUpdate(BaseModel):
    monthly_limit: MonthlyLimit


class BudgetRead(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    color: str
    icon: str
    monthly_limit: Decimal
    spent: Decimal
    # Negative once the limit is exceeded.
    remaining: Decimal
    used_pct: float
    status: BudgetStatus
    # Month-end spending at the pace so far; only for the month in progress.
    projected: Decimal | None


class BudgetReportRead(BaseModel):
    month: str
    start: date
    end: date
    # Day of the month reached so far, for the month in progress; otherwise None.
    days_elapsed: int | None
    days_in_period: int
    total_limit: Decimal
    total_spent: Decimal
    budgets: list[BudgetRead]
