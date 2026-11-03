from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import Category, CategoryRule, Transaction, User
from app.services.statements import import_statement

SAMPLE_DIR = Path(__file__).resolve().parents[3] / "sample_data"
NEW_CATEGORY = {"name": "Hobi", "color": "#123abc", "icon": "palette"}


@pytest.fixture
def other_user(db: Session) -> User:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    return other


def headers_for(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(str(user.id), 'access')}"}


def create_category(client: TestClient, headers: dict[str, str], **overrides: str) -> dict:
    response = client.post("/categories", headers=headers, json=NEW_CATEGORY | overrides)
    assert response.status_code == 201
    return response.json()


def default_category_id(db: Session, name: str) -> str:
    return str(
        db.scalar(select(Category.id).where(Category.user_id.is_(None), Category.name == name))
    )


def category_of(db: Session, description: str) -> str:
    return db.scalar(
        select(Category.name)
        .join(Transaction, Transaction.category_id == Category.id)
        .where(Transaction.description == description)
    )


def import_sample(db: Session, user: User, file_name: str) -> None:
    import_statement(db, user, file_name, (SAMPLE_DIR / file_name).read_bytes())


# --- categories ---


def test_list_returns_defaults_then_own(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_category(client, auth_headers)

    response = client.get("/categories", headers=auth_headers)

    body = response.json()
    assert len(body) == 15
    assert all(c["is_default"] for c in body[:14])
    assert body[-1]["name"] == "Hobi"
    assert body[-1]["is_default"] is False


def test_list_hides_other_users_categories(
    client: TestClient, auth_headers: dict[str, str], other_user: User
) -> None:
    create_category(client, headers_for(other_user))

    names = [c["name"] for c in client.get("/categories", headers=auth_headers).json()]

    assert "Hobi" not in names


@pytest.mark.parametrize("name", ["Hobi", "  hobi  ", "MARKET", "market"])
def test_duplicate_name_returns_409(
    client: TestClient, auth_headers: dict[str, str], name: str
) -> None:
    create_category(client, auth_headers)

    response = client.post("/categories", headers=auth_headers, json=NEW_CATEGORY | {"name": name})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "overrides",
    [{"name": "   "}, {"color": "red"}, {"color": "#12345"}, {"icon": "Bad Icon!"}],
)
def test_invalid_category_returns_422(
    client: TestClient, auth_headers: dict[str, str], overrides: dict[str, str]
) -> None:
    response = client.post("/categories", headers=auth_headers, json=NEW_CATEGORY | overrides)

    assert response.status_code == 422


def test_update_own_category(client: TestClient, auth_headers: dict[str, str]) -> None:
    category = create_category(client, auth_headers)

    response = client.patch(
        f"/categories/{category['id']}", headers=auth_headers, json={"color": "#000000"}
    )

    assert response.status_code == 200
    assert response.json()["color"] == "#000000"
    assert response.json()["name"] == "Hobi"


def test_default_categories_are_read_only(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    market = default_category_id(db, "Market")

    update = client.patch(f"/categories/{market}", headers=auth_headers, json={"name": "X"})
    delete = client.delete(f"/categories/{market}", headers=auth_headers)

    assert update.status_code == delete.status_code == 403


def test_other_users_category_is_not_found(
    client: TestClient, auth_headers: dict[str, str], other_user: User
) -> None:
    category = create_category(client, headers_for(other_user))

    update = client.patch(f"/categories/{category['id']}", headers=auth_headers, json={"name": "X"})
    delete = client.delete(f"/categories/{category['id']}", headers=auth_headers)

    assert update.status_code == delete.status_code == 404


def test_deleting_category_moves_transactions_to_other(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    category = create_category(client, auth_headers)
    client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": "STEAM", "category_id": category["id"]},
    )
    import_sample(db, user, "ornek_kredi_karti_2026_10.csv")
    assert category_of(db, "STEAM PURCHASE") == "Hobi"

    response = client.delete(f"/categories/{category['id']}", headers=auth_headers)

    assert response.status_code == 204
    assert category_of(db, "STEAM PURCHASE") == "Diğer"
    assert db.scalars(select(CategoryRule)).all() == []


# --- rules ---


def test_rule_is_applied_to_existing_transactions(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    import_sample(db, user, "ornek_hesap_ekstresi_2026_09.csv")
    category = create_category(client, auth_headers)

    response = client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": "starbucks", "category_id": category["id"]},
    )

    assert response.status_code == 201
    assert response.json()["updated_transactions"] == 2
    assert category_of(db, "STARBUCKS MODA") == "Hobi"


def test_rule_can_skip_existing_transactions(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    import_sample(db, user, "ornek_hesap_ekstresi_2026_09.csv")
    category = create_category(client, auth_headers)

    response = client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": "STARBUCKS", "category_id": category["id"], "apply_to_existing": False},
    )

    assert response.json()["updated_transactions"] == 0
    assert category_of(db, "STARBUCKS MODA") == "Yemek"


def test_rule_applies_to_later_imports(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": "KIRA", "category_id": default_category_id(db, "Faturalar")},
    )

    import_sample(db, user, "ornek_hesap_ekstresi_2026_09.csv")

    assert category_of(db, "KİRA ÖDEMESİ") == "Faturalar"


def test_saving_same_keyword_updates_existing_rule(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    for keyword, category in [("Migros", "Yemek"), ("MİGROS", "Alışveriş")]:
        client.post(
            "/category-rules",
            headers=auth_headers,
            json={"keyword": keyword, "category_id": default_category_id(db, category)},
        )

    rules = client.get("/category-rules", headers=auth_headers).json()

    assert len(rules) == 1
    assert rules[0]["keyword"] == "MİGROS"
    assert rules[0]["category_id"] == default_category_id(db, "Alışveriş")


def test_rule_with_other_users_category_returns_404(
    client: TestClient, auth_headers: dict[str, str], other_user: User
) -> None:
    category = create_category(client, headers_for(other_user))

    response = client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": "STEAM", "category_id": category["id"]},
    )

    assert response.status_code == 404


def test_rule_keyword_without_letters_returns_422(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    response = client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": " - . ", "category_id": default_category_id(db, "Market")},
    )

    assert response.status_code == 422


def test_delete_rule(client: TestClient, auth_headers: dict[str, str], db: Session) -> None:
    rule = client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": "STEAM", "category_id": default_category_id(db, "Market")},
    ).json()["rule"]

    response = client.delete(f"/category-rules/{rule['id']}", headers=auth_headers)

    assert response.status_code == 204
    assert client.get("/category-rules", headers=auth_headers).json() == []


def test_cannot_delete_other_users_rule(
    client: TestClient, auth_headers: dict[str, str], db: Session, other_user: User
) -> None:
    rule = client.post(
        "/category-rules",
        headers=headers_for(other_user),
        json={"keyword": "STEAM", "category_id": default_category_id(db, "Market")},
    ).json()["rule"]

    response = client.delete(f"/category-rules/{rule['id']}", headers=auth_headers)

    assert response.status_code == 404
