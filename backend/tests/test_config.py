import pytest
from pydantic import ValidationError

from app.core.config import Settings

SECRET = "x" * 32
PRODUCTION = {
    "environment": "production",
    "jwt_secret": SECRET,
    "database_url": "postgresql+psycopg://app:uzun-rastgele-sifre@db:5432/app",
    "frontend_url": "https://hesapkitap.example.com",
}


def settings(**values: str) -> Settings:
    return Settings(_env_file=None, **values)


def test_secure_production_settings_are_accepted() -> None:
    assert settings(**PRODUCTION).is_production


def test_production_refuses_the_development_database_password() -> None:
    values = {**PRODUCTION, "database_url": "postgresql+psycopg://harcamam:harcamam@db/harcamam"}

    with pytest.raises(ValidationError, match="development user and password"):
        settings(**values)


def test_production_requires_https_for_the_site() -> None:
    with pytest.raises(ValidationError, match="https"):
        settings(**{**PRODUCTION, "frontend_url": "http://hesapkitap.example.com"})


def test_production_images_can_be_tried_on_localhost() -> None:
    assert settings(**{**PRODUCTION, "frontend_url": "http://localhost"}).is_production


def test_development_keeps_its_defaults() -> None:
    assert not settings(jwt_secret=SECRET).is_production


def test_signing_key_is_required_everywhere() -> None:
    with pytest.raises(ValidationError):
        settings(jwt_secret="kisa")
