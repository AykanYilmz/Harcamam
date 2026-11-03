from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import INCOME_CATEGORY, OTHER_CATEGORY, Category, CategoryRule, User
from app.services.categorization.categorizer import Categorizer, KeywordRule
from app.services.categorization.default_rules import DEFAULT_KEYWORDS


def get_default_category(db: Session, name: str) -> Category:
    """A seeded default category; these always exist because a migration creates them."""
    return db.scalars(
        select(Category).where(Category.user_id.is_(None), Category.name == name)
    ).one()


def build_categorizer(db: Session, user: User) -> Categorizer:
    default_ids = {
        category.name: category.id
        for category in db.scalars(select(Category).where(Category.user_id.is_(None)))
    }
    default_rules = [
        KeywordRule(keyword, default_ids[category_name])
        for category_name, keywords in DEFAULT_KEYWORDS.items()
        for keyword in keywords
    ]
    # Newest first, so of two equally specific rules the one taught last wins.
    user_rules = [
        KeywordRule(rule.keyword, rule.category_id)
        for rule in db.scalars(
            select(CategoryRule)
            .where(CategoryRule.user_id == user.id)
            .order_by(CategoryRule.created_at.desc())
        )
    ]
    return Categorizer(
        user_rules,
        default_rules,
        income_category_id=default_ids[INCOME_CATEGORY],
        other_category_id=default_ids[OTHER_CATEGORY],
    )
