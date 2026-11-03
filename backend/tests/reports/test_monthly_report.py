from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import User
from app.services.statements import import_statement
from tests.reports.helpers import add_transactions

SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_data"

# September: income 10.000; spending 1.500 (Market) + 800 - 300 refund (Alışveriş) = 2.000.
# Transfers (-2.000 card payment, +5.000 incoming) are ignored.
# October: income 12.000; spending 1.800 (Market) + 400 (Yemek) = 2.200.
ROWS = [
    (date(2026, 9, 1), "MAAS", "10000", "Gelir"),
    (date(2026, 9, 3), "MIGROS", "-1000", "Market"),
    (date(2026, 9, 9), "BIM", "-500", "Market"),
    (date(2026, 9, 12), "TRENDYOL", "-800", "Alışveriş"),
    (date(2026, 9, 20), "TRENDYOL IADE", "300", "Alışveriş"),
    (date(2026, 9, 25), "KREDI KARTI ODEMESI", "-2000", "Transfer"),
    (date(2026, 9, 26), "GELEN HAVALE", "5000", "Transfer"),
    (date(2026, 10, 1), "MAAS", "12000", "Gelir"),
    (date(2026, 10, 4), "MIGROS", "-1800", "Market"),
    (date(2026, 10, 30), "YEMEKSEPETI", "-400", "Yemek"),
]


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


def get_report(client: TestClient, headers: dict[str, str], **params: str) -> dict:
    response = client.get("/reports/monthly", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()


def by_name(report: dict) -> dict[str, dict]:
    return {row["name"]: row for row in report["categories"]}


@pytest.mark.usefixtures("data")
def test_totals_exclude_transfers_and_net_refunds(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_report(client, auth_headers, month="2026-09")

    assert report["month"] == "2026-09"
    assert report["income"] == "10000.00"
    assert report["expense"] == "2000.00"
    assert report["net"] == "8000.00"
    assert report["transaction_count"] == 7
    assert {name: row["amount"] for name, row in by_name(report).items()} == {
        "Market": "1500.00",
        "Alışveriş": "500.00",
    }


@pytest.mark.usefixtures("data")
def test_comparison_with_previous_month(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get_report(client, auth_headers, month="2026-10")

    assert report["previous"] == {
        "month": "2026-09",
        "income": "10000.00",
        "expense": "2000.00",
        "net": "8000.00",
    }
    assert report["income_change_pct"] == 20.0
    assert report["expense_change_pct"] == 10.0
    # Net 9.800 vs 8.000
    assert report["net_change_pct"] == 22.5


@pytest.mark.usefixtures("data")
def test_categories_are_compared_and_sorted_by_amount(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_report(client, auth_headers, month="2026-10")

    assert [row["name"] for row in report["categories"]] == ["Market", "Yemek", "Alışveriş"]
    market, food, shopping = report["categories"]
    assert (market["amount"], market["previous_amount"]) == ("1800.00", "1500.00")
    assert (market["change_pct"], market["share_pct"]) == (20.0, 81.8)
    assert (food["change_pct"], food["share_pct"]) == (None, 18.2)
    # Present in the previous month only: shown as a drop to zero.
    assert (shopping["amount"], shopping["change_pct"]) == ("0.00", -100.0)


@pytest.mark.usefixtures("data")
def test_first_month_has_no_change_percentages(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_report(client, auth_headers, month="2026-09")

    assert report["previous"]["income"] == "0.00"
    assert report["income_change_pct"] is None
    assert report["expense_change_pct"] is None


@pytest.mark.usefixtures("data")
def test_defaults_to_latest_month_with_data(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert get_report(client, auth_headers)["month"] == "2026-10"


@pytest.mark.usefixtures("data")
def test_empty_month_is_all_zero(client: TestClient, auth_headers: dict[str, str]) -> None:
    report = get_report(client, auth_headers, month="2026-12")

    assert (report["income"], report["expense"], report["net"]) == ("0.00", "0.00", "0.00")
    assert report["categories"] == []
    assert report["transaction_count"] == 0


def test_user_without_transactions_gets_current_month(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    today = date.today()

    assert get_report(client, auth_headers)["month"] == f"{today.year:04d}-{today.month:02d}"


@pytest.mark.usefixtures("data")
def test_other_users_data_is_not_included(client: TestClient, db: Session) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    add_transactions(db, other, [(date(2026, 10, 2), "MIGROS", "-50", "Market")])
    headers = {"Authorization": f"Bearer {create_token(str(other.id), 'access')}"}

    report = get_report(client, headers, month="2026-10")

    assert report["expense"] == "50.00"
    assert report["previous"]["income"] == "0.00"


@pytest.mark.parametrize("month", ["2026-13", "2026-1", "26-10", "2026/10", "ekim"])
def test_invalid_month_returns_422(
    client: TestClient, auth_headers: dict[str, str], month: str
) -> None:
    response = client.get("/reports/monthly", headers=auth_headers, params={"month": month})

    assert response.status_code == 422


def test_sample_statements_october(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    for file_name in (
        "ornek_hesap_ekstresi_2026_09.csv",
        "ornek_hesap_ekstresi_2026_10.pdf",
        "ornek_kredi_karti_2026_10.csv",
    ):
        import_statement(db, user, file_name, (SAMPLE_DIR / file_name).read_bytes())

    report = get_report(client, auth_headers, month="2026-10")

    # Income: salary 45.000 + interest 92,10. Incoming havale and card payment are transfers.
    assert report["income"] == "45092.10"
    # Spending: 26.697,12 (PDF, October rows) + 10.433,28 (card) - 349 Trendyol refund.
    assert report["expense"] == "36781.40"
    assert report["net"] == "8310.70"
    assert report["transaction_count"] == 22 + 13
    assert report["previous"]["expense"] == "29160.72"
    assert report["expense_change_pct"] == 26.1

    categories = by_name(report)
    assert report["categories"][0]["name"] == "Kira"
    assert categories["Market"]["amount"] == "3705.75"
    assert categories["Market"]["previous_amount"] == "3043.45"
    assert categories["Market"]["change_pct"] == 21.8
    assert categories["Alışveriş"]["amount"] == "2898.00"
    assert "Transfer" not in categories
    assert "Gelir" not in categories
