import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Password = Annotated[str, Field(min_length=8, max_length=128)]


class UserCreate(BaseModel):
    email: EmailStr
    password: Password

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    created_at: datetime
    email_verified: bool
    # A new address waiting for its verification link to be opened.
    pending_email: EmailStr | None
    # Statement closing day that reports split months on; None means calendar months.
    period_end_day: int | None


class UserSettingsUpdate(BaseModel):
    """Fields left out are not changed."""

    period_end_day: Annotated[int, Field(ge=1, le=31)] | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: Password


class DeleteAccountRequest(BaseModel):
    # Asked again so an unattended, logged-in browser can't delete the account.
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class VerifyEmailResult(BaseModel):
    email: EmailStr


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    password: str
