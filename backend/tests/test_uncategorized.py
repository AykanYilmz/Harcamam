from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Transaction, User
from tests.reports.helpers import add_transactions

ROWS = [
    (date(2026, 9, 1), "ÖRNEK KASAP BOLU", "-300", "Diğer"),
    (date(2026, 9, 8), "ÖRNEK KASAP BOLU", "-200", "Diğer"),
    (date(2026, 9, 3), "PAYTR/ÖRNEK TEKNOLOJ İSTANBUL TR", "-6000", "Diğer"),
    (date(2026, 9, 4), "S/ÖRNEKBILET.COM İSTANB", "-1000", "Diğer"),
    (date(2026, 9, 9), "S/ÖRNEKBILET.COM İSTANB Satis Iade", "400", "Diğer"),
    (date(2026, 9, 5), "MIGROS KADIKÖY", "-150", "Market"),
]


def get_report(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.get("/transactions/uncategorized", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_groups_by_merchant_where_most_money_went_first(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    add_transactions(db, user, ROWS)

    report = get_report(client, auth_headers)

    assert report["transaction_count"] == 5
    assert [(m["name"], m["amount"], len(m["transactions"])) for m in report["merchants"]] == [
        ("ÖRNEK TEKNOLOJ", "6000.00", 1),
        # The refund lowers what went to the merchant.
        ("ÖRNEKBILET.COM", "600.00", 2),
        ("ÖRNEK KASAP", "500.00", 2),
    ]
    kasap = report["merchants"][2]
    assert [t["date"] for t in kasap["transactions"]] == ["2026-09-08", "2026-09-01"]


def test_leaves_out_what_the_user_put_in_other_by_hand(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    add_transactions(db, user, ROWS[:2])
    first = db.scalars(select(Transaction).where(Transaction.user_id == user.id)).first()
    first.is_manually_categorized = True
    db.flush()

    report = get_report(client, auth_headers)

    assert report["transaction_count"] == 1


def test_saving_the_keyword_as_a_rule_categorizes_the_whole_group(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    add_transactions(db, user, ROWS)
    bilet = next(
        m for m in get_report(client, auth_headers)["merchants"] if m["name"] == "ÖRNEKBILET.COM"
    )
    travel = db.scalar(select(Category.id).where(Category.name == "Ulaşım"))

    response = client.post(
        "/category-rules",
        headers=auth_headers,
        json={"keyword": bilet["keyword"], "category_id": str(travel)},
    )

    assert response.status_code == 201, response.text
    assert response.json()["updated_transactions"] == 2
    names = [m["name"] for m in get_report(client, auth_headers)["merchants"]]
    assert names == ["ÖRNEK TEKNOLOJ", "ÖRNEK KASAP"]


def test_other_users_transactions_are_not_listed(
    db: Session, user: User, client: TestClient, auth_headers: dict[str, str]
) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()
    add_transactions(db, other, ROWS)

    assert get_report(client, auth_headers) == {"transaction_count": 0, "merchants": []}
