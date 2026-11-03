from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import Category, Statement, Transaction, TransactionType, User
from app.services.statements import import_statement

SAMPLE_DIR = Path(__file__).resolve().parents[1].parent / "sample_data"
TOTAL = 26 + 13


@pytest.fixture(autouse=True)
def imported(db: Session, user: User) -> None:
    for file_name in ("ornek_hesap_ekstresi_2026_09.csv", "ornek_kredi_karti_2026_10.csv"):
        import_statement(db, user, file_name, (SAMPLE_DIR / file_name).read_bytes())


def category_id(db: Session, name: str) -> str:
    return str(db.scalar(select(Category.id).where(Category.name == name)))


def fetch(client: TestClient, headers: dict[str, str], **params: object) -> dict:
    response = client.get("/transactions", headers=headers, params=params)
    assert response.status_code == 200, response.text
    return response.json()


def descriptions(body: dict) -> list[str]:
    return [item["description"] for item in body["items"]]


def test_default_lists_all_newest_first(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = fetch(client, auth_headers)

    assert body["total"] == TOTAL
    assert body["page"] == 1
    assert body["pages"] == 1
    assert len(body["items"]) == TOTAL
    dates = [item["date"] for item in body["items"]]
    assert dates == sorted(dates, reverse=True)
    assert body["items"][0]["description"] == "APPLE.COM/BILL"


def test_pagination(client: TestClient, auth_headers: dict[str, str]) -> None:
    pages = [fetch(client, auth_headers, page=n, page_size=10) for n in (1, 2, 3, 4, 5)]

    assert [len(p["items"]) for p in pages] == [10, 10, 10, 9, 0]
    assert all(p["total"] == TOTAL and p["pages"] == 4 for p in pages)
    ids = [item["id"] for p in pages for item in p["items"]]
    assert len(set(ids)) == TOTAL


def test_date_range_is_inclusive(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = fetch(client, auth_headers, date_from="2026-09-01", date_to="2026-09-10")

    assert body["total"] == 11
    assert all("2026-09-01" <= item["date"] <= "2026-09-10" for item in body["items"])


def test_type_filter(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = fetch(client, auth_headers, type="income")

    assert sorted(descriptions(body)) == [
        "FAİZ GELİRİ",
        "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş.",
        "TRENDYOL İADE",
        "ÖNCEKİ DÖNEM ÖDEMESİ",
    ]


def test_single_and_multiple_category_filter(
    client: TestClient, auth_headers: dict[str, str], db: Session
) -> None:
    market = category_id(db, "Market")
    food = category_id(db, "Yemek")

    assert fetch(client, auth_headers, category_id=market)["total"] == 7
    assert fetch(client, auth_headers, category_id=[market, food])["total"] == 12


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("migros", 3),
        ("sok", 1),
        ("ŞOK", 1),
        ("istanbul", 3),
        ("İSTANBUL", 3),
        ("netflix.com", 1),
        ("yok-boyle-bir-sey", 0),
    ],
)
def test_text_search_ignores_case_and_turkish_letters(
    client: TestClient, auth_headers: dict[str, str], query: str, expected: int
) -> None:
    assert fetch(client, auth_headers, q=query)["total"] == expected


def test_like_wildcards_are_matched_literally(
    client: TestClient, auth_headers: dict[str, str], db: Session, user: User
) -> None:
    statement = db.scalars(select(Statement)).first()
    db.add(
        Transaction(
            user_id=user.id,
            statement_id=statement.id,
            date=date(2026, 9, 15),
            description="KAMPANYA %50_INDIRIM",
            amount=Decimal("10.00"),
            type=TransactionType.EXPENSE,
            fingerprint="x" * 64,
            category_id=category_id(db, "Diğer"),
        )
    )
    db.flush()

    assert descriptions(fetch(client, auth_headers, q="%")) == ["KAMPANYA %50_INDIRIM"]
    assert descriptions(fetch(client, auth_headers, q="_")) == ["KAMPANYA %50_INDIRIM"]
    assert fetch(client, auth_headers, q="%50_IND")["total"] == 1


@pytest.mark.parametrize(
    ("sort", "first"),
    [
        ("amount_desc", "MAAŞ ÖDEMESİ - ÖRNEK TEKNOLOJİ A.Ş."),
        ("amount_asc", "APPLE.COM/BILL"),
    ],
)
def test_sorting_by_amount(
    client: TestClient, auth_headers: dict[str, str], sort: str, first: str
) -> None:
    assert descriptions(fetch(client, auth_headers, sort=sort))[0] == first


def test_sorting_by_date_ascending(client: TestClient, auth_headers: dict[str, str]) -> None:
    dates = [item["date"] for item in fetch(client, auth_headers, sort="date_asc")["items"]]

    assert dates == sorted(dates)
    assert dates[0] == "2026-09-01"


def test_filters_combine(client: TestClient, auth_headers: dict[str, str], db: Session) -> None:
    body = fetch(
        client,
        auth_headers,
        type="expense",
        category_id=category_id(db, "Market"),
        q="migros",
        date_from="2026-10-01",
    )

    assert descriptions(body) == ["MIGROS SANAL MARKET"]


def test_other_users_transactions_are_not_listed(client: TestClient, db: Session) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    headers = {"Authorization": f"Bearer {create_token(str(other.id), 'access')}"}

    assert fetch(client, headers)["total"] == 0


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 101},
        {"date_from": "2026-10-01", "date_to": "2026-09-01"},
        {"sort": "random"},
        {"type": "both"},
        {"category_id": "not-a-uuid"},
        {"unknown": "x"},
    ],
)
def test_invalid_parameters_return_422(
    client: TestClient, auth_headers: dict[str, str], params: dict
) -> None:
    response = client.get("/transactions", headers=auth_headers, params=params)

    assert response.status_code == 422


def test_requires_authentication(client: TestClient) -> None:
    assert client.get("/transactions").status_code == 401
