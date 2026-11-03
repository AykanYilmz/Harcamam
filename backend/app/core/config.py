from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root, where the shared .env file lives (absent inside Docker; env vars are used there).
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    app_name: str = "HesapKitap API"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "postgresql+psycopg://harcamam:harcamam@localhost:5432/harcamam"

    # No default on purpose: the app must not start with a guessable signing key.
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    max_upload_size_bytes: int = 5 * 1024 * 1024

    # Where links in emails point to.
    frontend_url: str = "http://localhost:5173"

    # Defaults match the Mailpit container used in development (inbox at localhost:8025).
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = False
    email_from: str = "HesapKitap <no-reply@hesapkitap.local>"
    email_verification_expire_hours: int = 24
    # Minimum wait between two verification emails to the same user.
    verification_resend_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
