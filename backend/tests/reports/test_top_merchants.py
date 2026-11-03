from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, CategoryRule, User
from app.services.statements import import_statement
from tests.reports.helpers import add_transactions

SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_data"

ROWS = [
    (date(2026, 10, 1), "MAAS", "12000", "Gelir"),
    (date(2026, 10, 2), "MIGROS KADIKOY", "-1000", "Market"),
    (date(2026, 10, 3), "MIGROS SANAL MARKET", "-500", "Market"),
    (date(2026, 10, 4), "SHELL MASLAK", "-800", "Ulaşım"),
    (date(2026, 10, 5), "TRENDYOL", "-800", "Alışveriş"),
    (date(2026, 10, 6), "TRENDYOL IADE", "300", "Alışveriş"),
    (date(2026, 10, 7), "BILINMEYEN DUKKAN", "-200", "Diğer"),
    (date(2026, 10, 8), "Bilinmeyen  Dukkan", "-200", "Diğer"),
    (date(2026, 10, 9), "AMAZON IADE", "150", "Alışveriş"),
    (date(2026, 10, 10), "GIDEN HAVALE", "-5000", "Transfer"),
    (date(2026, 9, 30), "MIGROS KADIKOY", "-9999", "Market"),
]


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


def get_merchants(client: TestClient, headers: dict[str, str], **params: object) -> list[dict]:
    response = client.get("/reports/top-merchants", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()["merchants"]


def summary(merchants: list[dict]) -> list[tuple[str, str, int, str]]:
    return [(m["name"], m["amount"], m["transaction_count"], m["category_name"]) for m in merchants]


@pytest.mark.usefixtures("data")
def test_groups_by_matched_keyword_and_nets_refunds(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    merchants = get_merchants(client, auth_headers, month="2026-10")

    assert summary(merchants) == [
        ("MIGROS", "1500.00", 2, "Market"),
        ("SHELL", "800.00", 1, "Ulaşım"),
        ("TRENDYOL", "500.00", 2, "Alışveriş"),
        # No keyword matches: grouped by description, ignoring case and spacing.
        ("BILINMEYEN DUKKAN", "400.00", 2, "Diğer"),
    ]


@pytest.mark.usefixtures("data")
def test_limit(client: TestClient, auth_headers: dict[str, str]) -> None:
    merchants = get_merchants(client, auth_headers, month="2026-10", limit=2)

    assert [m["name"] for m in merchants] == ["MIGROS", "SHELL"]


@pytest.mark.usefixtures("data")
def test_user_rule_keyword_groups_merchants(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    market = db.scalar(select(Category.id).where(Category.name == "Market"))
    db.add(CategoryRule(user_id=user.id, keyword="Bilinmeyen", category_id=market))
    db.flush()

    names = [m["name"] for m in get_merchants(client, auth_headers, month="2026-10")]

    assert "Bilinmeyen" in names


@pytest.mark.usefixtures("data")
def test_defaults_to_latest_month(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/reports/top-merchants", headers=auth_headers)

    assert response.json()["month"] == "2026-10"


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 51}, {"month": "2026-00"}])
def test_invalid_parameters_return_422(
    client: TestClient, auth_headers: dict[str, str], params: dict
) -> None:
    response = client.get("/reports/top-merchants", headers=auth_headers, params=params)

    assert response.status_code == 422


def test_sample_statements_october(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    for file_name in ("ornek_hesap_ekstresi_2026_10.pdf", "ornek_kredi_karti_2026_10.csv"):
        import_statement(db, user, file_name, (SAMPLE_DIR / file_name).read_bytes())

    merchants = get_merchants(client, auth_headers, month="2026-10", limit=5)

    assert summary(merchants) == [
        ("KIRA", "15000.00", 1, "Kira"),
        ("PEGASUS", "2340.00", 1, "Ulaşım"),
        ("SHELL", "1900.00", 1, "Ulaşım"),
        ("ZARA", "1799.95", 1, "Giyim"),
        # MIGROS KADIKÖY İSTANBUL (1.088,40) + MIGROS SANAL MARKET (687,35)
        ("MIGROS", "1775.75", 2, "Market"),
    ]
