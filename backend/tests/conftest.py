import os
from collections.abc import Iterator
from pathlib import Path

# Must be set before the app is imported, because settings are read at import time.
os.environ.setdefault("JWT_SECRET", "test-secret-that-is-long-enough-for-hs256")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_token, hash_password
from app.main import app
from app.models import User

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_database_url() -> URL:
    """TEST_DATABASE_URL if given, otherwise the dev database URL pointed at `harcamam_test`."""
    if url := os.environ.get("TEST_DATABASE_URL"):
        return make_url(url)
    return make_url(get_settings().database_url).set(database="harcamam_test")


def create_database_if_missing(url: URL) -> None:
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin_engine.dispose()


def run_migrations(url: URL) -> None:
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option(
        "sqlalchemy.url", url.render_as_string(hide_password=False).replace("%", "%%")
    )
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = test_database_url()
    create_database_if_missing(url)

    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    run_migrations(url)

    yield engine
    engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    """A session whose changes are rolled back after each test, even if the code commits."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user(db: Session) -> User:
    user = User(email="test@example.com", password_hash=hash_password("guclu-sifre-123"))
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(str(user.id), 'access')}"}
