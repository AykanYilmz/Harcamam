from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from tests.reports.helpers import add_transactions

ROWS = [
    (date(2026, 8, 3), "MIGROS", "-1000", "Market"),
    (date(2026, 10, 4), "MIGROS", "-1500", "Market"),
    (date(2026, 10, 5), "BIM", "-500", "Market"),
    (date(2026, 9, 6), "YEMEKSEPETI", "-400", "Yemek"),
    (date(2026, 10, 7), "TRENDYOL", "-800", "Alışveriş"),
    (date(2026, 10, 8), "TRENDYOL IADE", "300", "Alışveriş"),
    (date(2026, 10, 1), "MAAS", "12000", "Gelir"),
    (date(2026, 10, 9), "KREDI KARTI ODEMESI", "-5000", "Transfer"),
    (date(2026, 5, 1), "SHELL", "-900", "Ulaşım"),
]


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


def get_trend(client: TestClient, headers: dict[str, str], **params: object) -> dict:
    response = client.get("/reports/category-trend", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.usefixtures("data")
def test_amounts_per_category_and_month(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get_trend(client, auth_headers, months=3, end="2026-10")

    assert report["months"] == ["2026-08", "2026-09", "2026-10"]
    rows = {c["name"]: (c["amounts"], c["total"]) for c in report["categories"]}
    assert rows == {
        "Market": (["1000.00", "0.00", "2000.00"], "3000.00"),
        # The refund lowers that month's spending.
        "Alışveriş": (["0.00", "0.00", "500.00"], "500.00"),
        "Yemek": (["0.00", "400.00", "0.00"], "400.00"),
    }


@pytest.mark.usefixtures("data")
def test_sorted_by_total_and_limited_to_spending(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    names = [
        c["name"] for c in get_trend(client, auth_headers, months=3, end="2026-10")["categories"]
    ]

    # Income, transfers and categories without spending in the period are not listed.
    assert names == ["Market", "Alışveriş", "Yemek"]


@pytest.mark.usefixtures("data")
def test_defaults_to_twelve_months_ending_at_latest_data(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_trend(client, auth_headers)

    assert len(report["months"]) == 12
    assert report["months"][-1] == "2026-10"
    assert "Ulaşım" in [c["name"] for c in report["categories"]]


@pytest.mark.usefixtures("data")
def test_matches_the_monthly_report(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get_trend(client, auth_headers, months=3, end="2026-10")
    monthly = client.get(
        "/reports/monthly", headers=auth_headers, params={"month": "2026-10"}
    ).json()

    october = {c["name"]: c["amounts"][-1] for c in report["categories"]}
    assert {name: amount for name, amount in october.items() if amount != "0.00"} == {
        c["name"]: c["amount"] for c in monthly["categories"] if c["amount"] != "0.00"
    }


@pytest.mark.parametrize("params", [{"months": 2}, {"months": 25}, {"end": "2026-13"}])
def test_invalid_parameters_return_422(
    client: TestClient, auth_headers: dict[str, str], params: dict
) -> None:
    response = client.get("/reports/category-trend", headers=auth_headers, params=params)

    assert response.status_code == 422
