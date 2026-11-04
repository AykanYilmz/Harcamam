from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import create_token
from app.demo.seed import reset_demo_account
from app.models import Category, CategoryRule, Statement, Transaction
from app.services.users import authenticate_user

EMAIL = "demo@example.com"
PASSWORD = "demo-sifre-123"


def headers_for(user_id: object) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(str(user_id), 'access')}"}


def test_demo_account_has_six_months_of_statements(db: Session, client: TestClient) -> None:
    user, results = reset_demo_account(db, EMAIL, PASSWORD)

    assert user.email_verified
    assert authenticate_user(db, EMAIL, PASSWORD) is not None
    assert len(results) == 7
    # October's account statement repeats September's last five transactions.
    assert results[5].skipped_duplicates == 5
    months = client.get(
        "/reports/trend", headers=headers_for(user.id), params={"months": 6, "end": "2026-10"}
    ).json()["months"]
    assert [m["month"] for m in months if m["expense"] != "0.00"] == [
        "2026-05",
        "2026-06",
        "2026-07",
        "2026-08",
        "2026-09",
        "2026-10",
    ]
    # Salary 30.000, a raise to 40.000 in June and to 45.000 in August (plus interest).
    assert [m["income"][:2] for m in months] == ["30", "40", "40", "45", "45", "45"]
    budgets = client.get(
        "/budgets", headers=headers_for(user.id), params={"month": "2026-10"}
    ).json()["budgets"]
    assert {b["name"]: b["status"] for b in budgets} == {
        "Ulaşım": "over",
        "Market": "warning",
        "Yemek": "ok",
        "Eğlence": "ok",
    }


def test_running_again_resets_the_account(db: Session) -> None:
    first, _ = reset_demo_account(db, EMAIL, PASSWORD)
    db.add(
        CategoryRule(
            user_id=first.id, keyword="BERBER", category_id=db.scalars(select(Category.id)).first()
        )
    )
    db.commit()

    second, results = reset_demo_account(db, EMAIL, PASSWORD)

    assert second.id != first.id
    count = db.scalar(
        select(func.count()).select_from(Transaction).where(Transaction.user_id == second.id)
    )
    assert count == sum(result.imported for result in results)
    assert db.scalar(select(func.count()).select_from(Statement)) == 7
    assert db.scalar(select(func.count()).select_from(CategoryRule)) == 0
