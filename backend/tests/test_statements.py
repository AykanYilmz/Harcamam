from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_token, hash_password
from app.models import Statement, Transaction, TransactionType, User

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_data"
SEPTEMBER_CSV = "ornek_hesap_ekstresi_2026_09.csv"
OCTOBER_PDF = "ornek_hesap_ekstresi_2026_10.pdf"
CARD_CSV = "ornek_kredi_karti_2026_10.csv"


def upload(
    client: TestClient,
    headers: dict[str, str],
    file_name: str,
    content: bytes | None = None,
    **form: str,
) -> Response:
    if content is None:
        content = (SAMPLE_DIR / file_name).read_bytes()
    return client.post(
        "/statements/upload", headers=headers, files={"file": (file_name, content)}, data=form
    )


def count_transactions(db: Session, **filters: object) -> int:
    query = select(func.count()).select_from(Transaction).filter_by(**filters)
    return db.scalar(query) or 0


@pytest.fixture
def other_user_headers(db: Session) -> dict[str, str]:
    other = User(email="baska@example.com", password_hash=hash_password("guclu-sifre-123"))
    db.add(other)
    db.flush()
    return {"Authorization": f"Bearer {create_token(str(other.id), 'access')}"}


# --- upload ---


def test_upload_csv_imports_transactions(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    response = upload(client, auth_headers, SEPTEMBER_CSV, bank_name="Örnek Bank")

    assert response.status_code == 201
    body = response.json()
    assert body["imported"] == 26
    assert body["skipped_duplicates"] == 0
    # The sample is built from known merchants; nothing is left for the user to sort out.
    assert body["uncategorized"] == 0
    assert body["statement"]["file_name"] == SEPTEMBER_CSV
    assert body["statement"]["bank_name"] == "Örnek Bank"
    assert body["statement"]["period_start"] == "2026-09-01"
    assert body["statement"]["period_end"] == "2026-09-30"
    assert body["statement"]["transaction_count"] == 26

    assert count_transactions(db, type=TransactionType.INCOME) == 2
    assert count_transactions(db, type=TransactionType.EXPENSE) == 24


def test_amounts_are_stored_positive_with_type(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)

    rent = db.scalars(select(Transaction).where(Transaction.description == "KİRA ÖDEMESİ")).one()
    assert rent.amount == Decimal("15000.00")
    assert rent.type is TransactionType.EXPENSE


def test_identical_transactions_in_one_file_are_all_kept(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)

    assert count_transactions(db, description="STARBUCKS MODA") == 2


def test_upload_pdf_imports_transactions(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = upload(client, auth_headers, OCTOBER_PDF)

    assert response.status_code == 201
    assert response.json()["imported"] == 27


def test_same_file_twice_returns_409(client: TestClient, auth_headers: dict[str, str]) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)

    response = upload(client, auth_headers, SEPTEMBER_CSV)

    assert response.status_code == 409


def test_overlapping_statement_skips_already_imported_transactions(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)

    response = upload(client, auth_headers, OCTOBER_PDF)

    assert response.status_code == 201
    assert response.json()["imported"] == 22
    assert response.json()["skipped_duplicates"] == 5
    assert count_transactions(db) == 26 + 22


def test_file_with_only_known_transactions_returns_409(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)
    subset = "Tarih;Açıklama;Tutar\n05.09.2026;NETFLIX.COM;-149,99 TL\n".encode()

    response = upload(client, auth_headers, "netflix.csv", subset)

    assert response.status_code == 409


def test_different_users_can_upload_the_same_file(
    client: TestClient, auth_headers: dict[str, str], other_user_headers: dict[str, str]
) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)

    response = upload(client, other_user_headers, SEPTEMBER_CSV)

    assert response.status_code == 201
    assert response.json()["imported"] == 26


def test_upload_requires_authentication(client: TestClient) -> None:
    response = upload(client, {}, SEPTEMBER_CSV)

    assert response.status_code == 401


# --- upload validation ---


@pytest.mark.parametrize(
    ("file_name", "content"),
    [
        ("ekstre.txt", b"Tarih;Aciklama;Tutar\n"),
        ("ekstre.xlsx", b"PK\x03\x04"),
        ("ekstre.pdf", b"Tarih;Aciklama;Tutar\n05.09.2026;BIM;-1,00\n"),
        ("ekstre.csv", b"%PDF-1.7 not a csv"),
    ],
)
def test_unsupported_or_mismatched_file_returns_415(
    client: TestClient, auth_headers: dict[str, str], file_name: str, content: bytes
) -> None:
    response = upload(client, auth_headers, file_name, content)

    assert response.status_code == 415


def test_too_large_file_returns_413(
    client: TestClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "max_upload_size_bytes", 100)

    response = upload(client, auth_headers, SEPTEMBER_CSV)

    assert response.status_code == 413


def test_empty_file_returns_422(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = upload(client, auth_headers, "bos.csv", b"")

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("file_name", "content", "message"),
    [
        ("liste.csv", b"Ad;Soyad\nAli;Veli\n", "columns"),
        ("bozuk.pdf", b"%PDF-1.4\ngarbage", "could not be opened"),
    ],
)
def test_unreadable_file_returns_422_with_reason(
    client: TestClient, auth_headers: dict[str, str], file_name: str, content: bytes, message: str
) -> None:
    response = upload(client, auth_headers, file_name, content)

    assert response.status_code == 422
    assert message in response.json()["detail"]


def test_file_name_is_stripped_of_directories(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    content = (SAMPLE_DIR / SEPTEMBER_CSV).read_bytes()

    response = upload(client, auth_headers, "../../etc/ekstre.csv", content)

    assert response.json()["statement"]["file_name"] == "ekstre.csv"


# --- list and delete ---


def test_list_returns_only_own_statements_with_counts(
    client: TestClient, auth_headers: dict[str, str], other_user_headers: dict[str, str]
) -> None:
    upload(client, auth_headers, SEPTEMBER_CSV)
    upload(client, auth_headers, CARD_CSV)
    upload(client, other_user_headers, OCTOBER_PDF)

    response = client.get("/statements", headers=auth_headers)

    assert response.status_code == 200
    counts = {s["file_name"]: s["transaction_count"] for s in response.json()}
    assert counts == {SEPTEMBER_CSV: 26, CARD_CSV: 13}


def test_statements_show_their_own_totals(client: TestClient, auth_headers: dict[str, str]) -> None:
    uploaded = upload(client, auth_headers, CARD_CSV).json()["statement"]

    listed = client.get("/statements", headers=auth_headers).json()[0]

    # The card's purchases, and its payment plus a refund.
    for statement in (uploaded, listed):
        assert (statement["money_out"], statement["money_in"]) == ("10433.28", "5349.00")


def test_delete_removes_statement_and_transactions(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    statement_id = upload(client, auth_headers, SEPTEMBER_CSV).json()["statement"]["id"]

    response = client.delete(f"/statements/{statement_id}", headers=auth_headers)

    assert response.status_code == 204
    assert db.scalar(select(func.count()).select_from(Statement)) == 0
    assert count_transactions(db) == 0
    assert upload(client, auth_headers, SEPTEMBER_CSV).status_code == 201


def test_cannot_delete_another_users_statement(
    client: TestClient, auth_headers: dict[str, str], other_user_headers: dict[str, str]
) -> None:
    statement_id = upload(client, auth_headers, SEPTEMBER_CSV).json()["statement"]["id"]

    response = client.delete(f"/statements/{statement_id}", headers=other_user_headers)

    assert response.status_code == 404
    assert len(client.get("/statements", headers=auth_headers).json()) == 1


def test_upload_reports_how_many_transactions_no_rule_recognized(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    content = "Tarih;Açıklama;Tutar\n01.10.2026;MIGROS;-100,00\n02.10.2026;ÖRNEK KASAP;-50,00\n"

    response = client.post(
        "/statements/upload",
        headers=auth_headers,
        files={"file": ("ekstre.csv", content.encode(), "text/csv")},
    )

    assert response.status_code == 201, response.text
    assert (response.json()["imported"], response.json()["uncategorized"]) == (2, 1)
