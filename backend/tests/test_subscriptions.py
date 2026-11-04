from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.models import User
from tests.reports.helpers import add_transactions

ROWS = [
    # Steady price, then a rise.
    (date(2026, 6, 5), "NETFLIX.COM", "-149.99", "Abonelikler"),
    (date(2026, 7, 5), "NETFLIX.COM", "-149.99", "Abonelikler"),
    (date(2026, 8, 5), "NETFLIX.COM", "-149.99", "Abonelikler"),
    (date(2026, 9, 5), "NETFLIX.COM", "-189.99", "Abonelikler"),
    # September's statement is missing: a two-month gap still counts.
    (date(2026, 6, 1), "KIRA ODEMESI", "-15000", "Kira"),
    (date(2026, 7, 1), "KIRA ODEMESI", "-15000", "Kira"),
    (date(2026, 8, 1), "KIRA ODEMESI", "-15000", "Kira"),
    (date(2026, 9, 30), "KIRA ODEMESI", "-15000", "Kira"),
    # Monthly but a little different every time: detected, never a "price rise".
    (date(2026, 7, 14), "ORNEK SU FATURASI", "-240", "Faturalar"),
    (date(2026, 8, 13), "ORNEK SU FATURASI", "-260", "Faturalar"),
    (date(2026, 9, 14), "ORNEK SU FATURASI", "-250", "Faturalar"),
    # Cancelled: nothing since June.
    (date(2026, 4, 10), "ORNEK SPOR SALONU", "-900", "Diğer"),
    (date(2026, 5, 10), "ORNEK SPOR SALONU", "-900", "Diğer"),
    (date(2026, 6, 10), "ORNEK SPOR SALONU", "-900", "Diğer"),
    # Not subscriptions:
    # a gas bill four times higher in winter,
    (date(2026, 1, 11), "IGDAS", "-1200", "Faturalar"),
    (date(2026, 2, 11), "IGDAS", "-900", "Faturalar"),
    (date(2026, 3, 11), "IGDAS", "-300", "Faturalar"),
    # weekly shopping,
    (date(2026, 9, 2), "MIGROS", "-500", "Market"),
    (date(2026, 9, 9), "MIGROS", "-480", "Market"),
    (date(2026, 9, 16), "MIGROS", "-510", "Market"),
    # only twice so far,
    (date(2026, 8, 6), "SPOTIFY", "-59.99", "Abonelikler"),
    (date(2026, 9, 6), "SPOTIFY", "-59.99", "Abonelikler"),
    # and income, however regular.
    (date(2026, 7, 1), "MAAS", "45000", "Gelir"),
    (date(2026, 8, 1), "MAAS", "45000", "Gelir"),
    (date(2026, 9, 1), "MAAS", "45000", "Gelir"),
]


def get_report(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.get("/subscriptions", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def data(db: Session, user: User) -> None:
    add_transactions(db, user, ROWS)


@pytest.mark.usefixtures("data")
def test_finds_monthly_payments_active_and_most_expensive_first(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    report = get_report(client, auth_headers)

    assert [(s["name"], s["active"]) for s in report["subscriptions"]] == [
        ("KIRA ODEMESI", True),
        ("ORNEK SU FATURASI", True),
        ("NETFLIX.COM", True),
        ("ORNEK SPOR SALONU", False),
    ]
    # Only active ones are counted.
    assert report["monthly_total"] == "15439.99"
    assert report["yearly_total"] == "185279.88"


@pytest.mark.usefixtures("data")
def test_reports_a_price_rise_and_the_next_charge(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    netflix = next(
        s for s in get_report(client, auth_headers)["subscriptions"] if s["name"] == "NETFLIX.COM"
    )

    assert (netflix["amount"], netflix["previous_amount"]) == ("189.99", "149.99")
    assert netflix["yearly_amount"] == "2279.88"
    assert (netflix["charge_count"], netflix["first_charge"], netflix["last_charge"]) == (
        4,
        "2026-06-05",
        "2026-09-05",
    )
    assert netflix["next_charge"] == "2026-10-05"
    assert netflix["category_name"] == "Abonelikler"


@pytest.mark.usefixtures("data")
def test_varying_bills_and_cancelled_ones_have_no_price_rise_or_next_charge(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    found = {s["name"]: s for s in get_report(client, auth_headers)["subscriptions"]}

    assert found["ORNEK SU FATURASI"]["previous_amount"] is None
    assert found["ORNEK SPOR SALONU"]["next_charge"] is None


@pytest.mark.usefixtures("data")
def test_dismiss_and_restore(client: TestClient, auth_headers: dict[str, str]) -> None:
    water = next(
        s
        for s in get_report(client, auth_headers)["subscriptions"]
        if s["name"] == "ORNEK SU FATURASI"
    )

    response = client.post(
        "/subscriptions/dismissed", headers=auth_headers, json={"key": water["key"]}
    )
    assert response.status_code == 204
    report = get_report(client, auth_headers)
    assert "ORNEK SU FATURASI" not in [s["name"] for s in report["subscriptions"]]
    assert report["dismissed"] == [{"key": water["key"], "name": "ORNEK SU FATURASI"}]
    assert report["monthly_total"] == "15189.99"

    response = client.delete(f"/subscriptions/dismissed/{water['key']}", headers=auth_headers)
    assert response.status_code == 204
    report = get_report(client, auth_headers)
    assert "ORNEK SU FATURASI" in [s["name"] for s in report["subscriptions"]]
    assert report["dismissed"] == []


@pytest.mark.usefixtures("data")
def test_only_detected_payments_can_be_dismissed(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/subscriptions/dismissed", headers=auth_headers, json={"key": "migros"})

    assert response.status_code == 404


@pytest.mark.usefixtures("data")
def test_other_users_see_nothing_of_it(db: Session, client: TestClient) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    headers = {"Authorization": f"Bearer {create_token(str(other.id), 'access')}"}

    assert get_report(client, headers) == {
        "monthly_total": "0.00",
        "yearly_total": "0.00",
        "subscriptions": [],
        "dismissed": [],
    }
