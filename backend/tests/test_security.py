import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import create_token, decode_token, hash_password, verify_password


def test_hash_password_does_not_store_plain_text() -> None:
    hashed = hash_password("guclu-sifre-123")

    assert hashed != "guclu-sifre-123"
    assert hashed.startswith("$argon2id$")


def test_verify_password() -> None:
    hashed = hash_password("guclu-sifre-123")

    assert verify_password("guclu-sifre-123", hashed)
    assert not verify_password("yanlis-sifre", hashed)


def test_same_password_hashes_differently() -> None:
    assert hash_password("guclu-sifre-123") != hash_password("guclu-sifre-123")


def test_decode_token_returns_subject() -> None:
    token = create_token("user-123", "access", version=3)

    claims = decode_token(token, expected_type="access")
    assert (claims.subject, claims.version) == ("user-123", 3)


def test_decode_token_rejects_wrong_type() -> None:
    token = create_token("user-123", "refresh")

    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token, expected_type="access")


def test_settings_reject_short_jwt_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(jwt_secret="too-short")
