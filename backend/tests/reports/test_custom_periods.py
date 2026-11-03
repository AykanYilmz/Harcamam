"""Reports for a user whose months end on their statement closing day (the 6th here)."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from tests.reports.helpers import add_transactions

ROWS = [
    (date(2026, 9, 6), "MIGROS", "-100", "Market"),  # last day of September's period
    (date(2026, 9, 7), "MIGROS", "-200", "Market"),  # first day of October's
    (date(2026, 9, 15), "MAAS", "10000", "Gelir"),
    (date(2026, 10, 6), "NETFLIX", "-50", "Abonelikler"),
    (date(2026, 10, 7), "MIGROS", "-400", "Market"),  # November's
]


@pytest.fixture
def data(db: Session, user: User) -> None:
    user.period_end_day = 6
    add_transactions(db, user, ROWS)


def get(client: TestClient, headers: dict[str, str], path: str, **params: object) -> dict:
    response = client.get(path, headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.usefixtures("data")
def test_monthly_report_covers_the_period(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get(client, auth_headers, "/reports/monthly", month="2026-10")

    assert (report["start"], report["end"]) == ("2026-09-07", "2026-10-06")
    assert report["income"] == "10000.00"
    assert report["expense"] == "250.00"
    assert report["transaction_count"] == 3
    assert {row["name"]: row["amount"] for row in report["categories"]} == {
        "Market": "200.00",
        "Abonelikler": "50.00",
    }
    previous = report["previous"]
    assert (previous["start"], previous["end"], previous["expense"]) == (
        "2026-08-07",
        "2026-09-06",
        "100.00",
    )


@pytest.mark.usefixtures("data")
def test_latest_month_is_the_period_of_the_latest_transaction(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # 7 October already belongs to November's period.
    assert get(client, auth_headers, "/reports/monthly")["month"] == "2026-11"


@pytest.mark.usefixtures("data")
def test_trend_groups_by_period(client: TestClient, auth_headers: dict[str, str]) -> None:
    months = get(client, auth_headers, "/reports/trend", months=3, end="2026-11")["months"]

    assert [(m["month"], m["start"], m["end"], m["expense"]) for m in months] == [
        ("2026-09", "2026-08-07", "2026-09-06", "100.00"),
        ("2026-10", "2026-09-07", "2026-10-06", "250.00"),
        ("2026-11", "2026-10-07", "2026-11-06", "400.00"),
    ]


@pytest.mark.usefixtures("data")
def test_category_trend_groups_by_period(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get(client, auth_headers, "/reports/category-trend", months=3, end="2026-11")

    market = next(row for row in report["categories"] if row["name"] == "Market")
    assert market["amounts"] == ["100.00", "200.00", "400.00"]


@pytest.mark.usefixtures("data")
def test_daily_lists_the_days_of_the_period(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    days = get(client, auth_headers, "/reports/daily", month="2026-10")["days"]

    assert (days[0]["date"], days[-1]["date"], len(days)) == ("2026-09-07", "2026-10-06", 30)
    assert days[0]["amount"] == "200.00"


@pytest.mark.usefixtures("data")
def test_top_merchants_within_the_period(client: TestClient, auth_headers: dict[str, str]) -> None:
    merchants = get(client, auth_headers, "/reports/top-merchants", month="2026-10")["merchants"]

    assert {m["name"]: m["amount"] for m in merchants} == {"MIGROS": "200.00", "NETFLIX": "50.00"}


@pytest.mark.usefixtures("data")
def test_daily_can_ask_for_the_calendar_month(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    days = get(client, auth_headers, "/reports/daily", month="2026-10", calendar_month=True)["days"]

    assert (days[0]["date"], days[-1]["date"]) == ("2026-10-01", "2026-10-31")
    assert {d["date"]: d["amount"] for d in days if d["amount"] != "0.00"} == {
        "2026-10-06": "50.00",
        "2026-10-07": "400.00",
    }
