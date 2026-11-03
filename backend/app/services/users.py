import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import DUMMY_PASSWORD_HASH, hash_password, verify_password
from app.models import User


class EmailAlreadyRegisteredError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


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
