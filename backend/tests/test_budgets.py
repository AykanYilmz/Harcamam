from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import Budget, Category, User
from app.services.budgets import budget_report
from tests.reports.helpers import add_transactions

ROWS = [
    (date(2026, 10, 2), "MIGROS", "-700", "Market"),
    (date(2026, 10, 9), "MIGROS", "-200", "Market"),
    (date(2026, 10, 5), "YEMEKSEPETI", "-850", "Yemek"),
    (date(2026, 10, 12), "TRENDYOL", "-1000", "Alışveriş"),
    (date(2026, 10, 20), "TRENDYOL IADE", "400", "Alışveriş"),
    (date(2026, 9, 28), "MIGROS", "-5000", "Market"),  # September: not counted
]


def category_id(db: Session, name: str) -> str:
    return str(db.scalar(select(Category.id).where(Category.name == name)))


def add_budget(
    client: TestClient, headers: dict[str, str], db: Session, name: str, limit: str
) -> str:
    response = client.post(
        "/budgets",
        headers=headers,
        json={"category_id": category_id(db, name), "monthly_limit": limit},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def get_report(client: TestClient, headers: dict[str, str], month: str = "2026-10") -> dict:
    response = client.get("/budgets", headers=headers, params={"month": month})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def budgets(db: Session, user: User, client: TestClient, auth_headers: dict[str, str]) -> None:
    add_transactions(db, user, ROWS)
    add_budget(client, auth_headers, db, "Market", "1000")
    add_budget(client, auth_headers, db, "Yemek", "800")
    add_budget(client, auth_headers, db, "Alışveriş", "2000")


@pytest.mark.usefixtures("budgets")
def test_report_measures_each_budget_and_puts_the_fullest_first(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_report(client, auth_headers)

    assert (report["start"], report["end"], report["days_in_period"]) == (
        "2026-10-01",
        "2026-10-31",
        31,
    )
    assert [
        (b["name"], b["spent"], b["remaining"], b["used_pct"], b["status"])
        for b in report["budgets"]
    ] == [
        ("Yemek", "850.00", "-50.00", 106.2, "over"),
        ("Market", "900.00", "100.00", 90.0, "warning"),
        # The refund lowers what counts against the budget.
        ("Alışveriş", "600.00", "1400.00", 30.0, "ok"),
    ]
    assert (report["total_limit"], report["total_spent"]) == ("3800.00", "2350.00")


@pytest.mark.usefixtures("budgets")
def test_a_finished_month_has_no_projection(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_report(client, auth_headers)

    assert report["days_elapsed"] is None
    assert {b["projected"] for b in report["budgets"]} == {None}


@pytest.mark.usefixtures("budgets")
def test_month_in_progress_projects_month_end_spending(db: Session, user: User) -> None:
    report = budget_report(db, user, date(2026, 10, 1), today=date(2026, 10, 10))

    market = next(u for u in report.usages if u.category.name == "Market")
    assert report.days_elapsed == 10
    # 900 in 10 days of a 31-day month.
    assert report.projected(market) == Decimal("2790.00")


@pytest.mark.usefixtures("budgets")
def test_budgets_follow_the_users_closing_day(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    user.period_end_day = 6
    db.flush()

    report = get_report(client, auth_headers)

    assert (report["start"], report["end"]) == ("2026-09-07", "2026-10-06")
    market = next(b for b in report["budgets"] if b["name"] == "Market")
    assert market["spent"] == "5700.00"


def test_budgets_without_spending_count_zero(
    db: Session, client: TestClient, auth_headers: dict[str, str]
) -> None:
    add_budget(client, auth_headers, db, "Kira", "15000")

    budget = get_report(client, auth_headers)["budgets"][0]

    assert (budget["spent"], budget["used_pct"], budget["status"]) == ("0.00", 0.0, "ok")


def test_change_and_remove_a_budget(
    db: Session, client: TestClient, auth_headers: dict[str, str]
) -> None:
    budget_id = add_budget(client, auth_headers, db, "Market", "1000")

    response = client.patch(
        f"/budgets/{budget_id}", headers=auth_headers, json={"monthly_limit": "1250.50"}
    )
    assert response.status_code == 204
    assert get_report(client, auth_headers)["budgets"][0]["monthly_limit"] == "1250.50"

    assert client.delete(f"/budgets/{budget_id}", headers=auth_headers).status_code == 204
    assert get_report(client, auth_headers)["budgets"] == []


def test_one_budget_per_category(
    db: Session, client: TestClient, auth_headers: dict[str, str]
) -> None:
    add_budget(client, auth_headers, db, "Market", "1000")

    response = client.post(
        "/budgets",
        headers=auth_headers,
        json={"category_id": category_id(db, "Market"), "monthly_limit": "2000"},
    )

    assert response.status_code == 409


@pytest.mark.parametrize("name", ["Gelir", "Transfer"])
def test_only_spending_can_be_budgeted(
    db: Session, client: TestClient, auth_headers: dict[str, str], name: str
) -> None:
    response = client.post(
        "/budgets",
        headers=auth_headers,
        json={"category_id": category_id(db, name), "monthly_limit": "1000"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("limit", ["0", "-50", "12.345", "abc"])
def test_limit_must_be_a_positive_amount(
    db: Session, client: TestClient, auth_headers: dict[str, str], limit: str
) -> None:
    response = client.post(
        "/budgets",
        headers=auth_headers,
        json={"category_id": category_id(db, "Market"), "monthly_limit": limit},
    )

    assert response.status_code == 422


def test_other_users_budgets_and_categories_are_off_limits(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    their_category = Category(user_id=other.id, name="Hobi", color="#123456", icon="tag")
    db.add(their_category)
    db.flush()
    their_budget = Budget(
        user_id=other.id, category_id=category_id(db, "Market"), monthly_limit=Decimal("500")
    )
    db.add(their_budget)
    db.flush()
    other_headers = {"Authorization": f"Bearer {create_token(str(other.id), 'access')}"}

    created = client.post(
        "/budgets",
        headers=auth_headers,
        json={"category_id": str(their_category.id), "monthly_limit": "100"},
    )
    assert created.status_code == 404
    path = f"/budgets/{their_budget.id}"
    assert client.patch(path, headers=auth_headers, json={"monthly_limit": "1"}).status_code == 404
    assert client.delete(path, headers=auth_headers).status_code == 404
    assert get_report(client, auth_headers)["budgets"] == []
    assert len(get_report(client, other_headers)["budgets"]) == 1


def test_deleting_a_category_deletes_its_budget(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    category = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "Hobi", "color": "#123456", "icon": "tag"},
    ).json()
    client.post(
        "/budgets",
        headers=auth_headers,
        json={"category_id": category["id"], "monthly_limit": "300"},
    )

    assert client.delete(f"/categories/{category['id']}", headers=auth_headers).status_code == 204

    assert get_report(client, auth_headers)["budgets"] == []
