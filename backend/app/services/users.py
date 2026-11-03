import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_email_token,
    decode_email_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.services.email import OutgoingEmail, email_change_notice, verification_email


class EmailAlreadyRegisteredError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class AlreadyVerifiedError(Exception):
    pass


class SameEmailError(Exception):
    pass


class InvalidVerificationLinkError(Exception):
    pass


class ResendTooSoonError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(f"Retry after {retry_after_seconds} seconds")
        self.retry_after_seconds = retry_after_seconds


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, email: str, password: str) -> User:
    if get_user_by_email(db, email) is not None:
        raise EmailAlreadyRegisteredError

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        # Another request registered the same email between our check and the insert.
        db.rollback()
        raise EmailAlreadyRegisteredError from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    """Set a new password and revoke every token issued so far (other sessions log out)."""
    if not verify_password(current_password, user.password_hash):
        raise WrongPasswordError
    user.password_hash = hash_password(new_password)
    user.token_version += 1
    db.commit()


def delete_account(db: Session, user: User, password: str) -> None:
    """Delete the user; the database cascades to their statements, transactions,
    categories and rules."""
    if not verify_password(password, user.password_hash):
        raise WrongPasswordError
    db.delete(user)
    db.commit()


# --- email verification ---


def _now() -> datetime:
    return datetime.now(UTC)


def _verification_email(user: User, email: str) -> OutgoingEmail:
    """The verification mail for `email`, and remember when it was sent."""
    token = create_email_token(str(user.id), email)
    link = f"{get_settings().frontend_url}/eposta-dogrula?{urlencode({'token': token})}"
    user.verification_sent_at = _now()
    return verification_email(email, link)


def start_verification(db: Session, user: User) -> OutgoingEmail:
    """The verification mail for a new account."""
    message = _verification_email(user, user.email)
    db.commit()
    return message


def resend_verification(db: Session, user: User) -> OutgoingEmail:
    """Send the link again: to the pending new address if a change waits, else to the
    current one. Raises AlreadyVerifiedError or ResendTooSoonError."""
    target = user.pending_email
    if target is None:
        if user.email_verified:
            raise AlreadyVerifiedError
        target = user.email

    wait = timedelta(seconds=get_settings().verification_resend_seconds)
    if user.verification_sent_at and _now() - user.verification_sent_at < wait:
        remaining = wait - (_now() - user.verification_sent_at)
        raise ResendTooSoonError(max(int(remaining.total_seconds()), 1))

    message = _verification_email(user, target)
    db.commit()
    return message


def request_email_change(
    db: Session, user: User, new_email: str, password: str
) -> list[OutgoingEmail]:
    """Park `new_email` until it is verified. Returns the mails to send: the link to the
    new address and a heads-up to the current one."""
    if not verify_password(password, user.password_hash):
        raise WrongPasswordError
    new_email = new_email.strip().lower()
    if new_email == user.email:
        raise SameEmailError
    if get_user_by_email(db, new_email) is not None:
        raise EmailAlreadyRegisteredError

    user.pending_email = new_email
    messages = [_verification_email(user, new_email), email_change_notice(user.email, new_email)]
    db.commit()
    return messages


def cancel_email_change(db: Session, user: User) -> None:
    # Any link already sent for it stops working: it no longer matches pending_email.
    user.pending_email = None
    db.commit()


def verify_email(db: Session, token: str) -> User:
    """Apply a verification link. Opening the same link twice is harmless.

    Raises InvalidVerificationLinkError (bad, expired or outdated link) or
    EmailAlreadyRegisteredError (someone else took the new address meanwhile).
    """
    try:
        subject, email = decode_email_token(token)
        user = get_user_by_id(db, uuid.UUID(subject))
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise InvalidVerificationLinkError from exc
    if user is None:
        raise InvalidVerificationLinkError

    if email == user.pending_email:
        if get_user_by_email(db, email) is not None:
            raise EmailAlreadyRegisteredError
        user.email = email
        user.pending_email = None
        user.email_verified_at = _now()
    elif email == user.email:
        if user.email_verified_at is None:
            user.email_verified_at = _now()
    else:
        # Sent for an address the account no longer has or wants.
        raise InvalidVerificationLinkError

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyRegisteredError from exc
    return user
