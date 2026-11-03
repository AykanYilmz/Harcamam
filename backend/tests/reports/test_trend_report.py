from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.services.reports import add_months
from tests.reports.helpers import add_transactions

ROWS = [
    (date(2026, 9, 1), "MAAS", "10000", "Gelir"),
    (date(2026, 9, 3), "MIGROS", "-1500", "Market"),
    (date(2026, 9, 20), "TRENDYOL IADE", "300", "Alışveriş"),
    (date(2026, 9, 25), "KREDI KARTI ODEMESI", "-2000", "Transfer"),
    (date(2026, 10, 1), "MAAS", "12000", "Gelir"),
    (date(2026, 10, 31), "MIGROS", "-2200", "Market"),
]


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


def get_trend(client: TestClient, headers: dict[str, str], **params: object) -> list[dict]:
    response = client.get("/reports/trend", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()["months"]


@pytest.mark.usefixtures("data")
def test_months_are_contiguous_and_empty_months_are_zero(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    months = get_trend(client, auth_headers, months=4, end="2026-11")

    assert [
        {key: month[key] for key in ("month", "income", "expense", "net")} for month in months
    ] == [
        {"month": "2026-08", "income": "0.00", "expense": "0.00", "net": "0.00"},
        # Refund lowers spending (1.500 - 300); the card payment is a transfer.
        {"month": "2026-09", "income": "10000.00", "expense": "1200.00", "net": "8800.00"},
        {"month": "2026-10", "income": "12000.00", "expense": "2200.00", "net": "9800.00"},
        {"month": "2026-11", "income": "0.00", "expense": "0.00", "net": "0.00"},
    ]
    assert (months[0]["start"], months[0]["end"]) == ("2026-08-01", "2026-08-31")


@pytest.mark.usefixtures("data")
def test_defaults_to_six_months_ending_at_latest_data(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    months = get_trend(client, auth_headers)

    assert [m["month"] for m in months] == [
        "2026-05",
        "2026-06",
        "2026-07",
        "2026-08",
        "2026-09",
        "2026-10",
    ]


@pytest.mark.usefixtures("data")
def test_matches_monthly_report(client: TestClient, auth_headers: dict[str, str]) -> None:
    trend = get_trend(client, auth_headers, months=3, end="2026-10")[-1]
    monthly = client.get(
        "/reports/monthly", headers=auth_headers, params={"month": "2026-10"}
    ).json()

    assert (trend["income"], trend["expense"]) == (monthly["income"], monthly["expense"])


def test_crosses_year_boundary(client: TestClient, auth_headers: dict[str, str]) -> None:
    months = get_trend(client, auth_headers, months=3, end="2027-01")

    assert [m["month"] for m in months] == ["2026-11", "2026-12", "2027-01"]


@pytest.mark.parametrize(
    ("month", "count", "expected"),
    [
        (date(2026, 10, 1), 1, date(2026, 11, 1)),
        (date(2026, 12, 1), 1, date(2027, 1, 1)),
        (date(2026, 1, 1), -1, date(2025, 12, 1)),
        (date(2026, 10, 1), -23, date(2024, 11, 1)),
    ],
)
def test_add_months(month: date, count: int, expected: date) -> None:
    assert add_months(month, count) == expected


@pytest.mark.parametrize("params", [{"months": 2}, {"months": 25}, {"end": "2026-13"}])
def test_invalid_parameters_return_422(
    client: TestClient, auth_headers: dict[str, str], params: dict
) -> None:
    response = client.get("/reports/trend", headers=auth_headers, params=params)

    assert response.status_code == 422
