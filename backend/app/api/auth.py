from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import CurrentUser, DbSession, user_from_token
from app.core.security import create_token
from app.models import User
from app.schemas.auth import (
    ChangeEmailRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    RefreshRequest,
    TokenPair,
    UserCreate,
    UserRead,
    UserSettingsUpdate,
    VerifyEmailRequest,
    VerifyEmailResult,
)
from app.services.email import EmailSender, get_email_sender
from app.services.users import (
    AlreadyVerifiedError,
    EmailAlreadyRegisteredError,
    InvalidVerificationLinkError,
    ResendTooSoonError,
    SameEmailError,
    WrongPasswordError,
    authenticate_user,
    cancel_email_change,
    change_password,
    create_user,
    delete_account,
    request_email_change,
    resend_verification,
    start_verification,
    verify_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])

Mailer = Annotated[EmailSender, Depends(get_email_sender)]
EMAIL_TAKEN = "Email is already registered"


def issue_tokens(user: User) -> TokenPair:
    subject = str(user.id)
    return TokenPair(
        access_token=create_token(subject, "access", user.token_version),
        refresh_token=create_token(subject, "refresh", user.token_version),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate, db: DbSession, mailer: Mailer, background_tasks: BackgroundTasks
) -> User:
    """Creates the account and emails a verification link. Verifying is not required to log in."""
    try:
        user = create_user(db, payload.email, payload.password)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN) from exc
    background_tasks.add_task(mailer.send, start_verification(db, user))
    return user


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


@router.patch("/me", response_model=UserRead)
def update_settings(payload: UserSettingsUpdate, current_user: CurrentUser, db: DbSession) -> User:
    for name, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, name, value)
    db.commit()
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


@router.post("/verify-email", response_model=VerifyEmailResult)
def confirm_email(payload: VerifyEmailRequest, db: DbSession) -> VerifyEmailResult:
    """Opened from the emailed link; works without being logged in (e.g. on a phone)."""
    try:
        user = verify_email(db, payload.token)
    except InvalidVerificationLinkError as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="The verification link is invalid or has expired"
        ) from exc
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN) from exc
    return VerifyEmailResult(email=user.email)


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
def resend_link(
    current_user: CurrentUser, db: DbSession, mailer: Mailer, background_tasks: BackgroundTasks
) -> None:
    try:
        message = resend_verification(db, current_user)
    except AlreadyVerifiedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email is already verified") from exc
    except ResendTooSoonError as exc:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting another email",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    background_tasks.add_task(mailer.send, message)


@router.post("/change-email", response_model=UserRead, status_code=status.HTTP_202_ACCEPTED)
def change_email(
    payload: ChangeEmailRequest,
    current_user: CurrentUser,
    db: DbSession,
    mailer: Mailer,
    background_tasks: BackgroundTasks,
) -> User:
    """Accepted, not done: the address changes once the link sent to it is opened."""
    try:
        messages = request_email_change(db, current_user, payload.new_email, payload.password)
    except WrongPasswordError as exc:
        raise WRONG_PASSWORD from exc
    except SameEmailError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail="This is already your email"
        ) from exc
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN) from exc
    for message in messages:
        background_tasks.add_task(mailer.send, message)
    return current_user


@router.delete("/pending-email", status_code=status.HTTP_204_NO_CONTENT)
def cancel_pending_email(current_user: CurrentUser, db: DbSession) -> None:
    cancel_email_change(db, current_user)
