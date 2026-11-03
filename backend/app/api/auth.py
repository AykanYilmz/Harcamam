from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import CurrentUser, DbSession, user_from_token
from app.core.security import create_token
from app.models import User
from app.schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserRead,
)
from app.services.users import (
    EmailAlreadyRegisteredError,
    WrongPasswordError,
    authenticate_user,
    change_password,
    create_user,
    delete_account,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def issue_tokens(user: User) -> TokenPair:
    subject = str(user.id)
    return TokenPair(
        access_token=create_token(subject, "access", user.token_version),
        refresh_token=create_token(subject, "refresh", user.token_version),
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
    return issue_tokens(user_from_token(db, payload.refresh_token, expected_type="refresh"))


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> User:
    return current_user


WRONG_PASSWORD = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="The password is incorrect"
)


@router.post("/change-password", response_model=TokenPair)
def update_password(
    payload: ChangePasswordRequest, current_user: CurrentUser, db: DbSession
) -> TokenPair:
    """Returns a new token pair: every token issued before, on any device, stops working."""
    try:
        change_password(db, current_user, payload.current_password, payload.new_password)
    except WrongPasswordError as exc:
        raise WRONG_PASSWORD from exc
    return issue_tokens(current_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def remove_account(payload: DeleteAccountRequest, current_user: CurrentUser, db: DbSession) -> None:
    try:
        delete_account(db, current_user, payload.password)
    except WrongPasswordError as exc:
        raise WRONG_PASSWORD from exc
