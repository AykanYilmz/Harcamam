import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import TokenType, decode_token
from app.models import User
from app.services.users import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def user_from_token(db: Session, token: str, expected_type: TokenType) -> User:
    """The token's user, if the token is valid and wasn't revoked by a version bump."""
    try:
        claims = decode_token(token, expected_type)
        user_id = uuid.UUID(claims.subject)
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise credentials_exception() from exc

    user = get_user_by_id(db, user_id)
    if user is None or claims.version != user.token_version:
        raise credentials_exception()
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    return user_from_token(db, token, expected_type="access")


CurrentUser = Annotated[User, Depends(get_current_user)]
