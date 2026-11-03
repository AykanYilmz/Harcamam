from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category


def get_default_category(db: Session, name: str) -> Category:
    """A seeded default category; these always exist because a migration creates them."""
    return db.scalars(
        select(Category).where(Category.user_id.is_(None), Category.name == name)
    ).one()
