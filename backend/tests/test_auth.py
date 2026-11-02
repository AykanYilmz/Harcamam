import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import User

EMAIL = "ayse@example.com"
PASSWORD = "guclu-sifre-123"


def register(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client: TestClient, email: str = EMAIL, password: str = PASSWORD):
    return client.post("/auth/login", data={"username": email, "password": password})


def tokens_for_new_user(client: TestClient) -> dict[str, str]:
    register(client)
    return login(client).json()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def make_token(
    subject: str,
    token_type: str,
    expires_in: timedelta,
    secret: str | None = None,
) -> str:
    settings = get_settings()
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(UTC) + expires_in,
    }
    return jwt.encode(payload, secret or settings.jwt_secret, algorithm=settings.jwt_algorithm)


# --- register ---


def test_register_creates_user(client: TestClient, db: Session) -> None:
    response = register(client, email="  Ayse@Example.COM ")

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == EMAIL
    assert "password" not in body
    assert "password_hash" not in body

    user = db.get(User, uuid.UUID(body["id"]))
    assert user is not None
    assert user.password_hash != PASSWORD


@pytest.mark.parametrize("email", [EMAIL, "AYSE@example.com"])
def test_register_duplicate_email_returns_409(client: TestClient, email: str) -> None:
    register(client)

    response = register(client, email=email)

    assert response.status_code == 409


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("not-an-email", PASSWORD),
        (EMAIL, "short"),
        (EMAIL, "x" * 129),
    ],
)
def test_register_rejects_invalid_input(client: TestClient, email: str, password: str) -> None:
    response = register(client, email=email, password=password)

    assert response.status_code == 422


# --- login ---


def test_login_returns_token_pair(client: TestClient) -> None:
    register(client)

    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


def test_login_email_is_case_insensitive(client: TestClient) -> None:
    register(client)

    response = login(client, email="AYSE@EXAMPLE.COM")

    assert response.status_code == 200


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    register(client)

    response = login(client, password="yanlis-sifre")

    assert response.status_code == 401


def test_login_does_not_reveal_whether_email_exists(client: TestClient) -> None:
    register(client)

    wrong_password = login(client, password="yanlis-sifre")
    unknown_email = login(client, email="kimse@example.com")

    assert unknown_email.status_code == wrong_password.status_code == 401
    assert unknown_email.json() == wrong_password.json()


# --- me ---


def test_me_returns_current_user(client: TestClient) -> None:
    tokens = tokens_for_new_user(client)

    response = client.get("/auth/me", headers=auth_header(tokens["access_token"]))

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_expired_token_returns_401(client: TestClient) -> None:
    user_id = register(client).json()["id"]
    expired = make_token(user_id, "access", expires_in=timedelta(minutes=-1))

    response = client.get("/auth/me", headers=auth_header(expired))

    assert response.status_code == 401


def test_me_with_token_signed_by_another_key_returns_401(client: TestClient) -> None:
    user_id = register(client).json()["id"]
    forged = make_token(
        user_id, "access", expires_in=timedelta(minutes=5), secret="attacker-secret-" + "x" * 32
    )

    response = client.get("/auth/me", headers=auth_header(forged))

    assert response.status_code == 401


def test_me_with_refresh_token_returns_401(client: TestClient) -> None:
    tokens = tokens_for_new_user(client)

    response = client.get("/auth/me", headers=auth_header(tokens["refresh_token"]))

    assert response.status_code == 401


def test_me_with_token_of_deleted_user_returns_401(client: TestClient, db: Session) -> None:
    tokens = tokens_for_new_user(client)
    db.query(User).delete()
    db.flush()

    response = client.get("/auth/me", headers=auth_header(tokens["access_token"]))

    assert response.status_code == 401


# --- refresh ---


def test_refresh_returns_working_tokens(client: TestClient) -> None:
    tokens = tokens_for_new_user(client)

    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    new_access = response.json()["access_token"]
    me = client.get("/auth/me", headers=auth_header(new_access))
    assert me.status_code == 200


def test_refresh_with_access_token_returns_401(client: TestClient) -> None:
    tokens = tokens_for_new_user(client)

    response = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})

    assert response.status_code == 401


def test_refresh_with_expired_token_returns_401(client: TestClient) -> None:
    user_id = register(client).json()["id"]
    expired = make_token(user_id, "refresh", expires_in=timedelta(seconds=-1))

    response = client.post("/auth/refresh", json={"refresh_token": expired})

    assert response.status_code == 401


def test_refresh_with_garbage_returns_401(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={"refresh_token": "not-a-jwt"})

    assert response.status_code == 401
