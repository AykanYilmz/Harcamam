from typing import Annotated

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.reports import (
    MONTH_PATTERN,
    CategorySpendingRead,
    CategoryTrendRead,
    CategoryTrendReportRead,
    DailySpendingRead,
    DaySpendingRead,
    MerchantSpendingRead,
    MonthlyReportRead,
    MonthTotalsRead,
    TopMerchantsRead,
    TrendReportRead,
)
from app.services import reports

router = APIRouter(prefix="/reports", tags=["reports"])

MonthParam = Annotated[
    str | None,
    Query(pattern=MONTH_PATTERN, description="YYYY-MM; defaults to the latest month with data"),
]


MIN_TREND_MONTHS = 3
MAX_TREND_MONTHS = 24
MAX_MERCHANTS = 50


def to_totals_read(totals: reports.MonthTotals) -> MonthTotalsRead:
    return MonthTotalsRead(
        month=reports.month_label(totals.month),
        start=totals.period.start,
        end=totals.period.end,
        income=totals.income,
        expense=totals.expense,
        net=totals.net,
    )


@router.get("/monthly", response_model=MonthlyReportRead)
def monthly(
    current_user: CurrentUser, db: DbSession, month: MonthParam = None
) -> MonthlyReportRead:
    report = reports.monthly_report(db, current_user, reports.parse_month(month) if month else None)
    current, previous = report.current, report.previous
    return MonthlyReportRead(
        month=reports.month_label(current.month),
        start=current.period.start,
        end=current.period.end,
        income=current.income,
        expense=current.expense,
        net=current.net,
        transaction_count=report.transaction_count,
        previous=to_totals_read(previous),
        income_change_pct=reports.change_pct(current.income, previous.income),
        expense_change_pct=reports.change_pct(current.expense, previous.expense),
        net_change_pct=reports.change_pct(current.net, previous.net),
        categories=[
            CategorySpendingRead(
                category_id=row.category.id,
                name=row.category.name,
                color=row.category.color,
                icon=row.category.icon,
                amount=row.amount,
                share_pct=reports.share_pct(row.amount, current.expense),
                previous_amount=row.previous_amount,
                change_pct=reports.change_pct(row.amount, row.previous_amount),
            )
            for row in report.categories
        ],
    )


@router.get("/trend", response_model=TrendReportRead)
def trend(
    current_user: CurrentUser,
    db: DbSession,
    months: Annotated[int, Query(ge=MIN_TREND_MONTHS, le=MAX_TREND_MONTHS)] = 6,
    end: MonthParam = None,
) -> TrendReportRead:
    last = reports.parse_month(end) if end else reports.latest_month(db, current_user)
    first = reports.add_months(last, -(months - 1))
    totals = reports.monthly_totals(db, current_user, first, last)
    return TrendReportRead(months=[to_totals_read(month) for month in totals])


@router.get("/top-merchants", response_model=TopMerchantsRead)
def top_merchants(
    current_user: CurrentUser,
    db: DbSession,
    month: MonthParam = None,
    limit: Annotated[int, Query(ge=1, le=MAX_MERCHANTS)] = 10,
) -> TopMerchantsRead:
    selected = reports.parse_month(month) if month else reports.latest_month(db, current_user)
    merchants = reports.top_merchants(db, current_user, selected, limit)
    return TopMerchantsRead(
        month=reports.month_label(selected),
        merchants=[
            MerchantSpendingRead(
                name=merchant.name,
                amount=merchant.amount,
                transaction_count=merchant.transaction_count,
                category_id=merchant.category.id,
                category_name=merchant.category.name,
            )
            for merchant in merchants
        ],
    )


@router.get("/daily", response_model=DailySpendingRead)
def daily(
    current_user: CurrentUser,
    db: DbSession,
    month: MonthParam = None,
    calendar_month: Annotated[
        bool, Query(description="Use the calendar month even if the user has a closing day")
    ] = False,
) -> DailySpendingRead:
    selected = reports.parse_month(month) if month else reports.latest_month(db, current_user)
    return DailySpendingRead(
        month=reports.month_label(selected),
        days=[
            DaySpendingRead(date=day, amount=amount)
            for day, amount in reports.daily_spending(db, current_user, selected, calendar_month)
        ],
    )


@router.get("/category-trend", response_model=CategoryTrendReportRead)
def category_trend(
    current_user: CurrentUser,
    db: DbSession,
    months: Annotated[int, Query(ge=MIN_TREND_MONTHS, le=MAX_TREND_MONTHS)] = 12,
    end: MonthParam = None,
) -> CategoryTrendReportRead:
    last = reports.parse_month(end) if end else reports.latest_month(db, current_user)
    first = reports.add_months(last, -(months - 1))
    return CategoryTrendReportRead(
        months=[
            reports.month_label(period.month)
            for period in reports.month_range(current_user, first, last)
        ],
        categories=[
            CategoryTrendRead(
                category_id=trend.category.id,
                name=trend.category.name,
                color=trend.category.color,
                icon=trend.category.icon,
                amounts=trend.amounts,
                total=trend.total,
            )
            for trend in reports.category_trend(db, current_user, first, last)
        ],
    )
