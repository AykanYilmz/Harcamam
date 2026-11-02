import uuid
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import CurrentUser, DbSession, credentials_exception
from app.core.security import create_token, decode_token
from app.models import User
from app.schemas.auth import RefreshRequest, TokenPair, UserCreate, UserRead
from app.services.users import (
    EmailAlreadyRegisteredError,
    authenticate_user,
    create_user,
    get_user_by_id,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def issue_tokens(user: User) -> TokenPair:
    subject = str(user.id)
    return TokenPair(
        access_token=create_token(subject, "access"),
        refresh_token=create_token(subject, "refresh"),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DbSession) -> User:
    try:
        return create_user(db, payload.email, payload.password)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered"
        ) from exc


@router.post("/login", response_model=TokenPair)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> TokenPair:
    # OAuth2 calls the field "username"; we use it for the email.
    user = authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    try:
        user_id = uuid.UUID(decode_token(payload.refresh_token, expected_type="refresh"))
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise credentials_exception() from exc

    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception()
    return issue_tokens(user)


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> User:
    return current_user
