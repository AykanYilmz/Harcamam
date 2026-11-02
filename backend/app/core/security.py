import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

TokenType = Literal["access", "refresh"]

password_hash = PasswordHash.recommended()

# Verified against when the email is unknown, so a failed login takes the same time either way.
DUMMY_PASSWORD_HASH = password_hash.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(subject: str, token_type: TokenType) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    if token_type == "access":
        expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    else:
        expires_at = now + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": expires_at,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: TokenType) -> str:
    """Return the token's subject. Raises jwt.InvalidTokenError if it is invalid or of the wrong type."""
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "type", "exp"]},
    )
    if payload["type"] != expected_type:
        raise jwt.InvalidTokenError(f"Expected a {expected_type} token")
    return payload["sub"]
