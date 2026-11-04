import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.reports import MonthParam
from app.core.dependencies import CurrentUser, DbSession
from app.schemas.budgets import (
    BudgetCreate,
    BudgetCreated,
    BudgetRead,
    BudgetReportRead,
    BudgetUpdate,
)
from app.services import budgets as service
from app.services import reports
from app.services.categories import CategoryNotFoundError

router = APIRouter(prefix="/budgets", tags=["budgets"])

BUDGET_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, detail="Budget not found")


def to_read(report: service.BudgetReport, usage: service.BudgetUsage) -> BudgetRead:
    return BudgetRead(
        id=usage.budget.id,
        category_id=usage.category.id,
        name=usage.category.name,
        color=usage.category.color,
        icon=usage.category.icon,
        monthly_limit=usage.budget.monthly_limit,
        spent=usage.spent,
        remaining=usage.remaining,
        used_pct=usage.used_pct,
        status=usage.status,
        projected=report.projected(usage),
    )


@router.get("", response_model=BudgetReportRead)
def list_budgets(
    current_user: CurrentUser, db: DbSession, month: MonthParam = None
) -> BudgetReportRead:
    selected = reports.parse_month(month) if month else reports.latest_month(db, current_user)
    report = service.budget_report(db, current_user, selected)
    return BudgetReportRead(
        month=reports.month_label(report.period.month),
        start=report.period.start,
        end=report.period.end,
        days_elapsed=report.days_elapsed,
        days_in_period=report.days_in_period,
        total_limit=sum((u.budget.monthly_limit for u in report.usages), reports.ZERO),
        total_spent=sum((u.spent for u in report.usages), reports.ZERO),
        budgets=[to_read(report, usage) for usage in report.usages],
    )


@router.post("", response_model=BudgetCreated, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, current_user: CurrentUser, db: DbSession) -> BudgetCreated:
    try:
        budget = service.create_budget(db, current_user, payload.category_id, payload.monthly_limit)
    except CategoryNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found") from exc
    except service.NotAnExpenseCategoryError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Only expense categories can have a budget",
        ) from exc
    except service.BudgetExistsError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="This category already has a budget"
        ) from exc
    return BudgetCreated(id=budget.id)


@router.patch("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_budget(
    budget_id: uuid.UUID, payload: BudgetUpdate, current_user: CurrentUser, db: DbSession
) -> None:
    try:
        service.update_budget(db, current_user, budget_id, payload.monthly_limit)
    except service.BudgetNotFoundError as exc:
        raise BUDGET_NOT_FOUND from exc


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    try:
        service.delete_budget(db, current_user, budget_id)
    except service.BudgetNotFoundError as exc:
        raise BUDGET_NOT_FOUND from exc
