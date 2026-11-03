from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Category, CategoryRule, Statement, Transaction, User
from app.services.statements import import_statement
from tests.reports.helpers import add_transactions

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_data"
PASSWORD = "guclu-sifre-123"
NEW_PASSWORD = "yeni-guclu-sifre-456"


def login(client: TestClient, password: str = PASSWORD) -> dict[str, str]:
    response = client.post(
        "/auth/login", data={"username": "test@example.com", "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def change_password(client: TestClient, token: str, current: str, new: str):
    return client.post(
        "/auth/change-password",
        headers=bearer(token),
        json={"current_password": current, "new_password": new},
    )


# --- change password ---


def test_change_password_returns_working_tokens(client: TestClient, user: User) -> None:
    tokens = login(client)

    response = change_password(client, tokens["access_token"], PASSWORD, NEW_PASSWORD)

    assert response.status_code == 200
    new_tokens = response.json()
    assert client.get("/auth/me", headers=bearer(new_tokens["access_token"])).status_code == 200
    assert login(client, NEW_PASSWORD)["access_token"]
    assert (
        client.post(
            "/auth/login", data={"username": "test@example.com", "password": PASSWORD}
        ).status_code
        == 401
    )


def test_change_password_revokes_existing_sessions(client: TestClient, user: User) -> None:
    other_device = login(client)
    this_device = login(client)

    change_password(client, this_device["access_token"], PASSWORD, NEW_PASSWORD)

    assert client.get("/auth/me", headers=bearer(other_device["access_token"])).status_code == 401
    refresh = client.post("/auth/refresh", json={"refresh_token": other_device["refresh_token"]})
    assert refresh.status_code == 401


def test_change_password_with_wrong_current_password_returns_400(
    client: TestClient, user: User
) -> None:
    tokens = login(client)

    response = change_password(client, tokens["access_token"], "yanlis-sifre", NEW_PASSWORD)

    assert response.status_code == 400
    assert client.get("/auth/me", headers=bearer(tokens["access_token"])).status_code == 200


def test_change_password_validates_new_password(client: TestClient, user: User) -> None:
    tokens = login(client)

    response = change_password(client, tokens["access_token"], PASSWORD, "kisa")

    assert response.status_code == 422


def test_tokens_without_version_count_as_version_zero(client: TestClient, user: User) -> None:
    # Tokens issued before versioning existed carry no "ver" claim.
    settings = get_settings()
    legacy = jwt.encode(
        {
            "sub": str(user.id),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    assert client.get("/auth/me", headers=bearer(legacy)).status_code == 200


# --- delete account ---


def test_delete_account_removes_all_user_data(
    client: TestClient, db: Session, user: User, auth_headers: dict[str, str]
) -> None:
    import_statement(
        db,
        user,
        "ornek_hesap_ekstresi_2026_09.csv",
        (SAMPLE_DIR / "ornek_hesap_ekstresi_2026_09.csv").read_bytes(),
    )
    # The user's own category with transactions in it: the cascade must handle the order.
    hobby = Category(user_id=user.id, name="Hobi", color="#000000", icon="tag")
    db.add(hobby)
    db.flush()
    db.add(CategoryRule(user_id=user.id, keyword="STEAM", category_id=hobby.id))
    add_transactions(db, user, [(date(2026, 9, 2), "STEAM", "-100", "Hobi")])

    response = client.request(
        "DELETE", "/auth/me", headers=auth_headers, json={"password": PASSWORD}
    )

    assert response.status_code == 204
    for model in (User, Statement, Transaction, CategoryRule):
        assert db.scalar(select(func.count()).select_from(model)) == 0
    assert db.scalar(select(func.count()).where(Category.user_id.is_not(None))) == 0
    # Default categories belong to nobody and stay.
    assert db.scalar(select(func.count()).select_from(Category)) == 14


def test_delete_account_requires_the_password(
    client: TestClient, db: Session, user: User, auth_headers: dict[str, str]
) -> None:
    response = client.request(
        "DELETE", "/auth/me", headers=auth_headers, json={"password": "yanlis-sifre"}
    )

    assert response.status_code == 400
    assert db.scalar(select(func.count()).select_from(User)) == 1


def test_deleted_users_tokens_stop_working(
    client: TestClient, user: User, auth_headers: dict[str, str]
) -> None:
    client.request("DELETE", "/auth/me", headers=auth_headers, json={"password": PASSWORD})

    assert client.get("/auth/me", headers=auth_headers).status_code == 401


# --- settings ---


def test_new_users_use_calendar_months(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get("/auth/me", headers=auth_headers).json()["period_end_day"] is None


def test_set_and_clear_the_closing_day(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.patch("/auth/me", headers=auth_headers, json={"period_end_day": 6})
    assert response.status_code == 200, response.text
    assert response.json()["period_end_day"] == 6
    assert client.get("/auth/me", headers=auth_headers).json()["period_end_day"] == 6

    response = client.patch("/auth/me", headers=auth_headers, json={"period_end_day": None})
    assert response.json()["period_end_day"] is None


def test_settings_left_out_are_not_changed(
    client: TestClient, auth_headers: dict[str, str], user: User
) -> None:
    user.period_end_day = 15

    response = client.patch("/auth/me", headers=auth_headers, json={})

    assert response.json()["period_end_day"] == 15


@pytest.mark.parametrize("day", [0, 32, -1, "altı"])
def test_closing_day_must_be_a_day_of_the_month(
    client: TestClient, auth_headers: dict[str, str], day: object
) -> None:
    response = client.patch("/auth/me", headers=auth_headers, json={"period_end_day": day})

    assert response.status_code == 422


def test_settings_require_login(client: TestClient) -> None:
    assert client.patch("/auth/me", json={"period_end_day": 6}).status_code == 401
