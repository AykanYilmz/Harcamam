import uuid
from dataclasses import dataclass
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


def create_token(subject: str, token_type: TokenType, version: int = 0) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    if token_type == "access":
        expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    else:
        expires_at = now + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": subject,
        "type": token_type,
        "ver": version,
        "iat": now,
        "exp": expires_at,
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


EMAIL_TOKEN_TYPE = "email_verify"


def create_email_token(subject: str, email: str) -> str:
    """A link token proving the user can read mail sent to `email`."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": EMAIL_TOKEN_TYPE,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=settings.email_verification_expire_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_email_token(token: str) -> tuple[str, str]:
    """Return (subject, email). Raises jwt.InvalidTokenError if invalid, expired or not an
    email token (so an access token can't be used here, nor this one as an access token)."""
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "type", "exp", "email"]},
    )
    if payload["type"] != EMAIL_TOKEN_TYPE:
        raise jwt.InvalidTokenError("Expected an email verification token")
    return payload["sub"], payload["email"]


@dataclass(frozen=True)
class TokenClaims:
    subject: str
    version: int


def decode_token(token: str, expected_type: TokenType) -> TokenClaims:
    """Raises jwt.InvalidTokenError if the token is invalid, expired or of the wrong type."""
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "type", "exp"]},
    )
    if payload["type"] != expected_type:
        raise jwt.InvalidTokenError(f"Expected a {expected_type} token")
    # Tokens issued before versioning existed count as version 0.
    return TokenClaims(subject=payload["sub"], version=payload.get("ver", 0))
