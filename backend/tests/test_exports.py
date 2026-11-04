import datetime as dt
import io

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import User
from tests.reports.helpers import add_transactions

ROWS = [
    (dt.date(2026, 9, 1), "MAAS", "45000", "Gelir"),
    (dt.date(2026, 9, 3), "MIGROS", "-1234.50", "Market"),
    (dt.date(2026, 9, 20), "KREDI KARTI ODEMESI", "-5000", "Transfer"),
    # Looks like a spreadsheet formula: must stay plain text.
    (dt.date(2026, 10, 2), '=HYPERLINK("http://example.com","tikla")', "-10", "Diğer"),
    (dt.date(2026, 10, 5), "YEMEKSEPETI", "-300", "Yemek"),
    (dt.date(2026, 11, 1), "MIGROS", "-999", "Market"),  # after the range
]
RANGE = {"start": "2026-09-01", "end": "2026-10-31"}


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


def export(client: TestClient, headers: dict[str, str], **params: str):
    return client.get("/exports/transactions", headers=headers, params={**RANGE, **params})


@pytest.mark.usefixtures("data")
def test_excel_has_transactions_monthly_and_category_sheets(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = export(client, auth_headers)

    assert response.status_code == 200
    assert response.headers["content-disposition"] == (
        'attachment; filename="hesapkitap_2026-09-01_2026-10-31.xlsx"'
    )
    workbook = load_workbook(io.BytesIO(response.content))
    assert workbook.sheetnames == ["İşlemler", "Aylık özet", "Kategoriler"]

    rows = list(workbook["İşlemler"].iter_rows(values_only=True))
    assert rows[0] == ("Tarih", "Açıklama", "Kategori", "Tür", "Tutar")
    assert len(rows) == 6
    assert rows[1] == (dt.datetime(2026, 9, 1), "MAAS", "Gelir", "Gelir", 45000)
    assert rows[2][1:] == ("MIGROS", "Market", "Gider", -1234.5)

    summary = list(workbook["Aylık özet"].iter_rows(values_only=True))
    # Transfers are left out of income and spending, as in the reports.
    assert [(row[0], row[3], row[4]) for row in summary[1:]] == [
        ("2026-09", 45000, 1234.5),
        ("2026-10", 0, 310),
    ]

    categories = list(workbook["Kategoriler"].iter_rows(values_only=True))
    assert categories[1:] == [("Market", 1234.5), ("Yemek", 300), ("Diğer", 10)]


@pytest.mark.usefixtures("data")
def test_excel_never_stores_a_description_as_a_formula(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    sheet = load_workbook(io.BytesIO(export(client, auth_headers).content))["İşlemler"]

    cell = next(row[1] for row in sheet.iter_rows(min_row=2) if "HYPERLINK" in str(row[1].value))
    assert cell.data_type == "s"
    assert cell.value == '=HYPERLINK("http://example.com","tikla")'


@pytest.mark.usefixtures("data")
def test_csv_opens_in_turkish_excel_and_neutralizes_formulas(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = export(client, auth_headers, format="csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    text = response.content.decode("utf-8")
    assert text.startswith("﻿")
    lines = text.lstrip("﻿").splitlines()
    assert lines[0] == "Tarih;Açıklama;Kategori;Tür;Tutar"
    assert lines[1] == "01.09.2026;MAAS;Gelir;Gelir;45.000,00"
    assert lines[2] == "03.09.2026;MIGROS;Market;Gider;-1.234,50"
    assert "'=HYPERLINK" in lines[4]
    assert len(lines) == 6


def test_range_must_be_valid(client: TestClient, auth_headers: dict[str, str]) -> None:
    backwards = export(client, auth_headers, start="2026-10-31", end="2026-09-01")
    too_long = export(client, auth_headers, start="2020-01-01", end="2026-10-31")

    assert (backwards.status_code, too_long.status_code) == (422, 422)


def test_export_needs_login(client: TestClient) -> None:
    assert client.get("/exports/transactions", params=RANGE).status_code == 401


@pytest.mark.usefixtures("data")
def test_other_users_transactions_are_not_exported(db: Session, client: TestClient) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    headers = {"Authorization": f"Bearer {create_token(str(other.id), 'access')}"}

    lines = export(client, headers, format="csv").content.decode("utf-8").splitlines()

    assert len(lines) == 1


def test_browsers_may_read_the_file_name_cross_origin(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = export(client, {**auth_headers, "Origin": "http://localhost:5173"})

    assert "content-disposition" in response.headers["access-control-expose-headers"].lower()
