"""Creates, or resets, the demo account and fills it with the fake statements.

    python -m app.demo                       # demo@hesapkitap.dev / demo12345
    python -m app.demo --email ... --password ...

Running it again deletes the account and everything in it first, so a public demo can be
reset (e.g. nightly) to a known state, whatever visitors changed.
"""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.demo.statements import (
    ACCOUNT_OCTOBER,
    OCTOBER_OPENING,
    account_csv,
    account_csvs,
    card_csv,
)
from app.models import Category, User
from app.services.budgets import create_budget
from app.services.statements import ImportResult, import_statement
from app.services.users import create_user, get_user_by_email

DEMO_EMAIL = "demo@hesapkitap.dev"
DEMO_PASSWORD = "demo12345"

# Chosen so October shows every state: Market close to its limit, Ulaşım over, others fine.
DEMO_BUDGETS = {"Market": "4000", "Ulaşım": "5000", "Yemek": "1500", "Eğlence": "500"}


def _statement_files() -> list[tuple[str, bytes]]:
    files = [(name, text.encode("utf-8")) for name, text in account_csvs()]
    # Overlaps September's last days on purpose: the duplicates are skipped, as in real use.
    october = account_csv(ACCOUNT_OCTOBER, "26.09.2026 - 31.10.2026", OCTOBER_OPENING)
    files.append(("ornek_hesap_ekstresi_2026_10.csv", october.encode("utf-8")))
    files.append(("ornek_kredi_karti_2026_10.csv", card_csv().encode("cp1254")))
    return files


def reset_demo_account(
    db: Session, email: str = DEMO_EMAIL, password: str = DEMO_PASSWORD
) -> tuple[User, list[ImportResult]]:
    if existing := get_user_by_email(db, email):
        # The database cascades to the account's statements, transactions, categories and rules.
        db.delete(existing)
        db.commit()

    user = create_user(db, email, password)
    # Verified, so visitors don't see the "verify your email" reminder.
    user.email_verified_at = datetime.now(UTC)
    db.commit()

    results = [import_statement(db, user, name, content) for name, content in _statement_files()]
    for name, limit in DEMO_BUDGETS.items():
        category_id = db.scalar(
            select(Category.id).where(Category.user_id.is_(None), Category.name == name)
        )
        create_budget(db, user, category_id, Decimal(limit))
    return user, results
