from functools import lru_cache
from pathlib import Path
from typing import Self
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root, where the shared .env file lives (absent inside Docker; env vars are used there).
ROOT_DIR = Path(__file__).resolve().parents[3]

# The development defaults; a production database must not be reachable with these.
DEV_DATABASE_CREDENTIALS = "harcamam:harcamam@"
LOCAL_HOSTS = {"localhost", "127.0.0.1"}


class InsecureProductionSettingsError(ValueError):
    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    app_name: str = "HesapKitap API"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]
    # Path prefix a reverse proxy serves the API under ("/api" in production), so the docs
    # page links to the right OpenAPI URL. The proxy strips it before passing requests on.
    root_path: str = ""

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

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def refuse_insecure_production(self) -> Self:
        """Fail at startup rather than run in production with development settings.

        `localhost` stays allowed for the site address, so the production images can be tried
        on one machine; anything else must be served over https.
        """
        if not self.is_production:
            return self
        problems = []
        if DEV_DATABASE_CREDENTIALS in self.database_url:
            problems.append("DATABASE_URL uses the development user and password")
        site = urlsplit(self.frontend_url)
        if site.scheme != "https" and site.hostname not in LOCAL_HOSTS:
            problems.append("FRONTEND_URL must be an https:// address")
        if problems:
            raise InsecureProductionSettingsError("; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
