from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from tests.reports.helpers import add_transactions

ROWS = [
    (date(2026, 2, 1), "MAAS", "12000", "Gelir"),
    (date(2026, 2, 3), "MIGROS", "-1000", "Market"),
    (date(2026, 2, 3), "YEMEKSEPETI", "-250", "Yemek"),
    (date(2026, 2, 10), "TRENDYOL", "-800", "Alışveriş"),
    (date(2026, 2, 10), "TRENDYOL IADE", "300", "Alışveriş"),
    (date(2026, 2, 15), "KREDI KARTI ODEMESI", "-5000", "Transfer"),
    (date(2026, 2, 28), "SHELL", "-900", "Ulaşım"),
    (date(2026, 3, 1), "MIGROS", "-75", "Market"),
]


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


def get_daily(client: TestClient, headers: dict[str, str], **params: str) -> dict:
    response = client.get("/reports/daily", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.usefixtures("data")
def test_every_day_of_the_month_is_listed(client: TestClient, auth_headers: dict[str, str]) -> None:
    days = get_daily(client, auth_headers, month="2026-02")["days"]

    assert len(days) == 28
    assert days[0]["date"] == "2026-02-01"
    assert days[-1]["date"] == "2026-02-28"


@pytest.mark.usefixtures("data")
def test_daily_amounts_follow_report_rules(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    days = {
        d["date"]: d["amount"] for d in get_daily(client, auth_headers, month="2026-02")["days"]
    }

    # Income ("Gelir") and transfers are not spending.
    assert days["2026-02-01"] == "0.00"
    assert days["2026-02-15"] == "0.00"
    assert days["2026-02-03"] == "1250.00"
    # The refund lowers that day's spending.
    assert days["2026-02-10"] == "500.00"
    assert days["2026-02-28"] == "900.00"


@pytest.mark.usefixtures("data")
def test_daily_total_matches_monthly_report(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    days = get_daily(client, auth_headers, month="2026-02")["days"]
    monthly = client.get(
        "/reports/monthly", headers=auth_headers, params={"month": "2026-02"}
    ).json()

    assert sum(float(d["amount"]) for d in days) == float(monthly["expense"])


@pytest.mark.usefixtures("data")
def test_defaults_to_latest_month(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get_daily(client, auth_headers)

    assert report["month"] == "2026-03"
    assert len(report["days"]) == 31


def test_invalid_month_returns_422(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/reports/daily", headers=auth_headers, params={"month": "2026-2"})

    assert response.status_code == 422
