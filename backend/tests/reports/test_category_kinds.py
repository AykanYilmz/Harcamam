"""Reports follow each category's kind, so users' own income and transfer categories count right."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Category, CategoryKind, User
from tests.reports.helpers import add_transactions


@pytest.fixture
def user_categories(db: Session, user: User) -> dict[str, Category]:
    categories = {
        "Freelance": Category(
            user_id=user.id, name="Freelance", color="#000000", icon="x", kind=CategoryKind.INCOME
        ),
        "Birikim": Category(
            user_id=user.id, name="Birikim", color="#000000", icon="x", kind=CategoryKind.TRANSFER
        ),
    }
    db.add_all(categories.values())
    db.flush()
    add_transactions(
        db,
        user,
        [
            (date(2026, 10, 1), "MAAS", "12000", "Gelir"),
            (date(2026, 10, 5), "PROJE ODEMESI", "3000", "Freelance"),
            # An expense in an income category lowers income (e.g. a platform fee).
            (date(2026, 10, 6), "PLATFORM KOMISYONU", "-500", "Freelance"),
            (date(2026, 10, 7), "BIRIKIM HESABINA", "-4000", "Birikim"),
            (date(2026, 10, 8), "MIGROS", "-1000", "Market"),
        ],
    )
    return categories


def monthly(client: TestClient, headers: dict[str, str]) -> dict:
    return client.get("/reports/monthly", headers=headers, params={"month": "2026-10"}).json()


@pytest.mark.usefixtures("user_categories")
def test_user_income_category_counts_as_income(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = monthly(client, auth_headers)

    assert report["income"] == "14500.00"
    assert [row["name"] for row in report["categories"]] == ["Market"]


@pytest.mark.usefixtures("user_categories")
def test_user_transfer_category_is_excluded(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = monthly(client, auth_headers)
    trend = client.get(
        "/reports/trend", headers=auth_headers, params={"months": 3, "end": "2026-10"}
    ).json()["months"][-1]
    merchants = client.get(
        "/reports/top-merchants", headers=auth_headers, params={"month": "2026-10"}
    ).json()["merchants"]

    assert report["expense"] == trend["expense"] == "1000.00"
    assert [m["name"] for m in merchants] == ["MIGROS"]


def test_changing_kind_changes_reports(
    client: TestClient, auth_headers: dict[str, str], user_categories: dict[str, Category]
) -> None:
    freelance = user_categories["Freelance"]
    client.patch(f"/categories/{freelance.id}", headers=auth_headers, json={"kind": "expense"})

    report = monthly(client, auth_headers)

    # As an expense category, Freelance's 3.000 income now counts as a refund against its
    # 500 fee: spending 1.000 (Market) - 2.500 (Freelance) = -1.500.
    assert report["income"] == "12000.00"
    assert report["expense"] == "-1500.00"
