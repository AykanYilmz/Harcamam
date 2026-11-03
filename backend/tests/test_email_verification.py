import re
from datetime import UTC, datetime, timedelta
from urllib.parse import unquote

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_email_token
from app.models import User
from tests.conftest import FakeEmailSender

EMAIL = "ayse@example.com"
NEW_EMAIL = "ayse.yeni@example.com"
PASSWORD = "guclu-sifre-123"


def register(client: TestClient, email: str = EMAIL) -> None:
    response = client.post("/auth/register", json={"email": email, "password": PASSWORD})
    assert response.status_code == 201, response.text


def login(client: TestClient, email: str = EMAIL) -> dict[str, str]:
    response = client.post("/auth/login", data={"username": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def link_token(outbox: FakeEmailSender, to: str) -> str:
    """The token in the latest verification link sent to `to`."""
    mail = next(m for m in reversed(outbox.sent) if m.to == to and "token=" in m.body)
    match = re.search(r"/eposta-dogrula\?token=(\S+)", mail.body)
    assert match, mail.body
    return unquote(match.group(1))


def verify(client: TestClient, token: str):
    return client.post("/auth/verify-email", json={"token": token})


def me(client: TestClient, headers: dict[str, str]) -> dict:
    return client.get("/auth/me", headers=headers).json()


def allow_resend_now(db: Session, email: str = EMAIL) -> None:
    user = db.query(User).filter_by(email=email).one()
    user.verification_sent_at = datetime.now(UTC) - timedelta(minutes=5)
    db.flush()


# --- registration and verification ---


def test_register_sends_a_verification_link(client: TestClient, outbox: FakeEmailSender) -> None:
    register(client)

    assert [mail.to for mail in outbox.sent] == [EMAIL]
    assert get_settings().frontend_url + "/eposta-dogrula?token=" in outbox.sent[0].body
    assert me(client, login(client))["email_verified"] is False


def test_unverified_users_can_use_the_app(client: TestClient) -> None:
    register(client)

    response = client.get("/transactions", headers=login(client))

    assert response.status_code == 200


def test_link_verifies_the_email(client: TestClient, outbox: FakeEmailSender) -> None:
    register(client)

    response = verify(client, link_token(outbox, EMAIL))

    assert response.status_code == 200
    assert response.json() == {"email": EMAIL}
    assert me(client, login(client))["email_verified"] is True


def test_opening_the_link_twice_is_harmless(client: TestClient, outbox: FakeEmailSender) -> None:
    register(client)
    token = link_token(outbox, EMAIL)
    verify(client, token)

    assert verify(client, token).status_code == 200


def test_expired_link_is_rejected(client: TestClient, outbox: FakeEmailSender, db: Session) -> None:
    register(client)
    user = db.query(User).filter_by(email=EMAIL).one()
    settings = get_settings()
    expired = jwt.encode(
        {
            "sub": str(user.id),
            "type": "email_verify",
            "email": EMAIL,
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    assert verify(client, expired).status_code == 400


@pytest.mark.parametrize("token", ["", "not-a-jwt"])
def test_garbage_link_is_rejected(client: TestClient, token: str) -> None:
    assert verify(client, token).status_code == 400


def test_tokens_cannot_be_swapped(client: TestClient, outbox: FakeEmailSender) -> None:
    register(client)
    headers = login(client)
    access_token = headers["Authorization"].removeprefix("Bearer ")
    email_token = link_token(outbox, EMAIL)

    assert verify(client, access_token).status_code == 400
    assert (
        client.get("/auth/me", headers={"Authorization": f"Bearer {email_token}"}).status_code
        == 401
    )


# --- resending ---


def test_resend_waits_a_minute(client: TestClient, outbox: FakeEmailSender, db: Session) -> None:
    register(client)
    headers = login(client)

    too_soon = client.post("/auth/resend-verification", headers=headers)
    assert too_soon.status_code == 429
    assert 0 < int(too_soon.headers["Retry-After"]) <= 60

    allow_resend_now(db)
    assert client.post("/auth/resend-verification", headers=headers).status_code == 204
    assert len(outbox.sent) == 2


def test_resend_after_verification_returns_409(client: TestClient, outbox: FakeEmailSender) -> None:
    register(client)
    verify(client, link_token(outbox, EMAIL))

    response = client.post("/auth/resend-verification", headers=login(client))

    assert response.status_code == 409


# --- changing the email ---


def change_email(client: TestClient, headers: dict[str, str], new_email: str, password=PASSWORD):
    return client.post(
        "/auth/change-email",
        headers=headers,
        json={"new_email": new_email, "password": password},
    )


def test_change_email_waits_for_the_new_address(
    client: TestClient, outbox: FakeEmailSender
) -> None:
    register(client)
    headers = login(client)

    response = change_email(client, headers, "  Ayse.Yeni@Example.com ")

    assert response.status_code == 202
    assert response.json()["email"] == EMAIL
    assert response.json()["pending_email"] == NEW_EMAIL
    # A link to the new address and a heads-up to the current one.
    assert [mail.to for mail in outbox.sent[-2:]] == [NEW_EMAIL, EMAIL]
    assert NEW_EMAIL in outbox.sent[-1].body
    # Until then, the old address is still the login.
    login(client, EMAIL)


def test_verifying_the_new_address_switches_the_login(
    client: TestClient, outbox: FakeEmailSender
) -> None:
    register(client)
    change_email(client, login(client), NEW_EMAIL)

    response = verify(client, link_token(outbox, NEW_EMAIL))

    assert response.json() == {"email": NEW_EMAIL}
    profile = me(client, login(client, NEW_EMAIL))
    assert profile["email_verified"] is True
    assert profile["pending_email"] is None
    assert (
        client.post("/auth/login", data={"username": EMAIL, "password": PASSWORD}).status_code
        == 401
    )


def test_change_email_requires_the_password(client: TestClient) -> None:
    register(client)

    response = change_email(client, login(client), NEW_EMAIL, password="yanlis-sifre")

    assert response.status_code == 400


def test_change_to_own_email_returns_422(client: TestClient) -> None:
    register(client)

    assert change_email(client, login(client), EMAIL.upper()).status_code == 422


def test_change_to_a_taken_email_returns_409(client: TestClient) -> None:
    register(client, NEW_EMAIL)
    register(client, EMAIL)

    assert change_email(client, login(client), NEW_EMAIL).status_code == 409


def test_cancelled_change_invalidates_its_link(client: TestClient, outbox: FakeEmailSender) -> None:
    register(client)
    headers = login(client)
    change_email(client, headers, NEW_EMAIL)
    token = link_token(outbox, NEW_EMAIL)

    assert client.delete("/auth/pending-email", headers=headers).status_code == 204

    assert verify(client, token).status_code == 400
    assert me(client, headers)["email"] == EMAIL


def test_a_newer_change_invalidates_the_older_link(
    client: TestClient, outbox: FakeEmailSender, db: Session
) -> None:
    register(client)
    headers = login(client)
    change_email(client, headers, NEW_EMAIL)
    old_token = link_token(outbox, NEW_EMAIL)
    change_email(client, headers, "ayse.baska@example.com")

    assert verify(client, old_token).status_code == 400


def test_address_taken_before_verification_returns_409(
    client: TestClient, outbox: FakeEmailSender
) -> None:
    register(client)
    change_email(client, login(client), NEW_EMAIL)
    token = link_token(outbox, NEW_EMAIL)
    register(client, NEW_EMAIL)

    assert verify(client, token).status_code == 409


def test_resend_during_a_change_goes_to_the_new_address(
    client: TestClient, outbox: FakeEmailSender, db: Session
) -> None:
    register(client)
    headers = login(client)
    change_email(client, headers, NEW_EMAIL)
    allow_resend_now(db)

    client.post("/auth/resend-verification", headers=headers)

    assert outbox.sent[-1].to == NEW_EMAIL


def test_email_token_for_another_user_cannot_verify_this_one(
    client: TestClient, db: Session
) -> None:
    register(client)
    register(client, NEW_EMAIL)
    other = db.query(User).filter_by(email=NEW_EMAIL).one()
    # A link signed for the other account but naming this account's address.
    token = create_email_token(str(other.id), EMAIL)

    assert verify(client, token).status_code == 400
