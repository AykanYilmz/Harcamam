from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import Category, Transaction, User
from app.schemas.transactions import MAX_BULK_UPDATE
from app.services.statements import import_statement

SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_data"


@pytest.fixture
def imported(db: Session, user: User) -> None:
    content = (SAMPLE_DIR / "ornek_hesap_ekstresi_2026_09.csv").read_bytes()
    import_statement(db, user, "ornek_hesap_ekstresi_2026_09.csv", content)


@pytest.fixture
def other_user(db: Session) -> User:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    return other


def category_id(db: Session, name: str) -> str:
    return str(db.scalar(select(Category.id).where(Category.name == name)))


def transactions_with(db: Session, description: str) -> list[Transaction]:
    return list(db.scalars(select(Transaction).where(Transaction.description == description)))


def transaction_id(db: Session, description: str) -> str:
    return str(transactions_with(db, description)[0].id)


def category_name(db: Session, transaction: Transaction) -> str:
    db.refresh(transaction)
    return db.scalar(select(Category.name).where(Category.id == transaction.category_id))


# --- single correction ---


@pytest.mark.usefixtures("imported")
def test_correction_sets_category_and_manual_flag(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    tx_id = transaction_id(db, "TRENDYOL")

    response = client.patch(
        f"/transactions/{tx_id}",
        headers=auth_headers,
        json={"category_id": category_id(db, "Giyim")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transaction"]["category_id"] == category_id(db, "Giyim")
    assert body["transaction"]["is_manually_categorized"] is True
    assert body["transaction"]["amount"] == "1129.00"
    assert body["rule"] is None
    assert body["updated_transactions"] == 0


@pytest.mark.usefixtures("imported")
def test_correction_with_rule_updates_similar_transactions(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    first, second = transactions_with(db, "STARBUCKS MODA")

    response = client.patch(
        f"/transactions/{first.id}",
        headers=auth_headers,
        json={"category_id": category_id(db, "Eğlence"), "rule_keyword": "STARBUCKS"},
    )

    body = response.json()
    assert body["rule"]["keyword"] == "STARBUCKS"
    assert body["updated_transactions"] == 1
    assert category_name(db, first) == category_name(db, second) == "Eğlence"
    db.refresh(second)
    assert first.is_manually_categorized is True
    assert second.is_manually_categorized is False


@pytest.mark.usefixtures("imported")
def test_rule_does_not_override_manual_corrections(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    corrected, other = transactions_with(db, "MIGROS KADIKÖY İSTANBUL")
    client.patch(
        f"/transactions/{corrected.id}",
        headers=auth_headers,
        json={"category_id": category_id(db, "Yemek")},
    )

    client.patch(
        f"/transactions/{transaction_id(db, 'A101 MODA')}",
        headers=auth_headers,
        json={"category_id": category_id(db, "Alışveriş"), "rule_keyword": "MIGROS"},
    )

    assert category_name(db, corrected) == "Yemek"
    assert category_name(db, other) == "Alışveriş"


@pytest.mark.usefixtures("imported")
def test_correcting_another_users_transaction_returns_404(
    client: TestClient, db: Session, other_user: User
) -> None:
    other_headers = {"Authorization": f"Bearer {create_token(str(other_user.id), 'access')}"}

    response = client.patch(
        f"/transactions/{transaction_id(db, 'TRENDYOL')}",
        headers=other_headers,
        json={"category_id": category_id(db, "Giyim")},
    )

    assert response.status_code == 404


@pytest.mark.usefixtures("imported")
def test_correcting_to_another_users_category_returns_404(
    client: TestClient, auth_headers: dict[str, str], db: Session, other_user: User
) -> None:
    foreign = Category(user_id=other_user.id, name="Gizli", color="#000000", icon="x")
    db.add(foreign)
    db.flush()

    response = client.patch(
        f"/transactions/{transaction_id(db, 'TRENDYOL')}",
        headers=auth_headers,
        json={"category_id": str(foreign.id)},
    )

    assert response.status_code == 404
    assert category_name(db, transactions_with(db, "TRENDYOL")[0]) == "Alışveriş"


@pytest.mark.usefixtures("imported")
def test_invalid_rule_keyword_rejects_whole_correction(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    response = client.patch(
        f"/transactions/{transaction_id(db, 'TRENDYOL')}",
        headers=auth_headers,
        json={"category_id": category_id(db, "Giyim"), "rule_keyword": "--"},
    )

    assert response.status_code == 422
    transaction = transactions_with(db, "TRENDYOL")[0]
    assert category_name(db, transaction) == "Alışveriş"
    assert transaction.is_manually_categorized is False


def test_correction_requires_authentication(client: TestClient, db: Session) -> None:
    response = client.patch(
        "/transactions/00000000-0000-0000-0000-000000000000",
        json={"category_id": category_id(db, "Giyim")},
    )

    assert response.status_code == 401


# --- bulk ---


@pytest.mark.usefixtures("imported")
def test_bulk_update_sets_category_for_all(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    ids = [transaction_id(db, d) for d in ("TRENDYOL", "LC WAIKIKI", "CINEMAXIMUM")]

    response = client.patch(
        "/transactions/bulk",
        headers=auth_headers,
        json={"transaction_ids": ids, "category_id": category_id(db, "Alışveriş")},
    )

    assert response.status_code == 200
    assert response.json() == {"updated": 3}
    for description in ("TRENDYOL", "LC WAIKIKI", "CINEMAXIMUM"):
        transaction = transactions_with(db, description)[0]
        assert category_name(db, transaction) == "Alışveriş"
        assert transaction.is_manually_categorized is True


@pytest.mark.usefixtures("imported")
def test_bulk_update_with_foreign_id_changes_nothing(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    ids = [transaction_id(db, "TRENDYOL"), "00000000-0000-0000-0000-000000000000"]

    response = client.patch(
        "/transactions/bulk",
        headers=auth_headers,
        json={"transaction_ids": ids, "category_id": category_id(db, "Giyim")},
    )

    assert response.status_code == 404
    assert category_name(db, transactions_with(db, "TRENDYOL")[0]) == "Alışveriş"


@pytest.mark.parametrize("count", [0, MAX_BULK_UPDATE + 1])
def test_bulk_update_rejects_empty_or_oversized_lists(
    client: TestClient, auth_headers: dict[str, str], db: Session, count: int
) -> None:
    ids = ["00000000-0000-0000-0000-000000000000"] * count

    response = client.patch(
        "/transactions/bulk",
        headers=auth_headers,
        json={"transaction_ids": ids, "category_id": category_id(db, "Giyim")},
    )

    assert response.status_code == 422
