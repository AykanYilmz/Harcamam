import uuid

from sqlalchemy import ColumnElement, func, or_, select, update
from sqlalchemy.orm import Session

from app.models import (
    INCOME_CATEGORY,
    OTHER_CATEGORY,
    Category,
    CategoryKind,
    CategoryRule,
    Transaction,
    User,
)
from app.services.categorization.categorizer import Categorizer, KeywordRule
from app.services.categorization.default_rules import DEFAULT_KEYWORDS
from app.services.parsing.formats import normalize_description, normalize_text


class CategoryNotFoundError(Exception):
    pass


class DefaultCategoryReadOnlyError(Exception):
    pass


class CategoryNameTakenError(Exception):
    pass


class RuleNotFoundError(Exception):
    pass


class InvalidKeywordError(Exception):
    pass


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


def recategorize_transactions(db: Session, user: User) -> int:
    """Re-run the categorizer on the user's automatically categorized transactions.

    Returns how many changed. Manually categorized transactions are never touched.
    """
    categorizer = build_categorizer(db, user)
    changed = 0
    for transaction in db.scalars(
        select(Transaction).where(
            Transaction.user_id == user.id, Transaction.is_manually_categorized.is_(False)
        )
    ):
        category_id = categorizer.categorize(transaction.description, transaction.type)
        if category_id != transaction.category_id:
            transaction.category_id = category_id
            changed += 1
    return changed


# --- categories ---


def _visible_to(user: User) -> ColumnElement[bool]:
    return or_(Category.user_id.is_(None), Category.user_id == user.id)


def list_categories(db: Session, user: User) -> list[Category]:
    """Default categories first, then the user's own, each alphabetically."""
    return list(
        db.scalars(
            select(Category)
            .where(_visible_to(user))
            .order_by(Category.user_id.is_not(None), Category.name)
        )
    )


def get_accessible_category(db: Session, user: User, category_id: uuid.UUID) -> Category | None:
    """A default category or one of the user's own; never another user's."""
    return db.scalar(select(Category).where(Category.id == category_id, _visible_to(user)))


def _get_own_category(db: Session, user: User, category_id: uuid.UUID) -> Category:
    category = get_accessible_category(db, user, category_id)
    if category is None:
        raise CategoryNotFoundError
    if category.is_default:
        raise DefaultCategoryReadOnlyError
    return category


def _ensure_name_available(
    db: Session, user: User, name: str, exclude_id: uuid.UUID | None = None
) -> None:
    query = select(Category.id).where(_visible_to(user), func.lower(Category.name) == name.lower())
    if exclude_id is not None:
        query = query.where(Category.id != exclude_id)
    if db.scalar(query) is not None:
        raise CategoryNameTakenError


def create_category(
    db: Session,
    user: User,
    name: str,
    color: str,
    icon: str,
    kind: CategoryKind = CategoryKind.EXPENSE,
) -> Category:
    _ensure_name_available(db, user, name)
    category = Category(user_id=user.id, name=name, color=color, icon=icon, kind=kind)
    db.add(category)
    db.commit()
    return category


def update_category(
    db: Session,
    user: User,
    category_id: uuid.UUID,
    name: str | None = None,
    color: str | None = None,
    icon: str | None = None,
    kind: CategoryKind | None = None,
) -> Category:
    category = _get_own_category(db, user, category_id)
    if name is not None:
        _ensure_name_available(db, user, name, exclude_id=category.id)
        category.name = name
    if color is not None:
        category.color = color
    if icon is not None:
        category.icon = icon
    if kind is not None:
        category.kind = kind
    db.commit()
    return category


def delete_category(db: Session, user: User, category_id: uuid.UUID) -> None:
    """Delete one of the user's categories; its transactions move to "Diğer"."""
    category = _get_own_category(db, user, category_id)
    other = get_default_category(db, OTHER_CATEGORY)
    db.execute(
        update(Transaction)
        .where(Transaction.user_id == user.id, Transaction.category_id == category.id)
        .values(category_id=other.id)
    )
    db.delete(category)
    db.commit()


# --- rules ---


def list_rules(db: Session, user: User) -> list[CategoryRule]:
    return list(
        db.scalars(
            select(CategoryRule)
            .where(CategoryRule.user_id == user.id)
            .order_by(CategoryRule.created_at.desc())
        )
    )


def validate_keyword(keyword: str) -> str:
    """Return the cleaned keyword, or raise InvalidKeywordError if it can never match."""
    keyword = normalize_description(keyword)
    if not normalize_text(keyword):
        raise InvalidKeywordError
    return keyword


def save_rule(
    db: Session,
    user: User,
    keyword: str,
    category_id: uuid.UUID,
    apply_to_existing: bool = True,
) -> tuple[CategoryRule, int]:
    """Create the rule, or update the user's rule with the same keyword.

    Returns the rule and how many existing transactions it re-categorized. The caller is
    responsible for committing, so a correction and its rule are saved together.
    """
    keyword = validate_keyword(keyword)
    matching_key = normalize_text(keyword)
    if get_accessible_category(db, user, category_id) is None:
        raise CategoryNotFoundError

    # "Migros" and "MIGROS" are the same rule.
    rule = next(
        (r for r in list_rules(db, user) if normalize_text(r.keyword) == matching_key), None
    )
    if rule is None:
        rule = CategoryRule(user_id=user.id, keyword=keyword, category_id=category_id)
        db.add(rule)
    else:
        rule.keyword = keyword
        rule.category_id = category_id
    db.flush()

    updated = recategorize_transactions(db, user) if apply_to_existing else 0
    return rule, updated


def delete_rule(db: Session, user: User, rule_id: uuid.UUID) -> None:
    rule = db.scalar(
        select(CategoryRule).where(CategoryRule.id == rule_id, CategoryRule.user_id == user.id)
    )
    if rule is None:
        raise RuleNotFoundError
    db.delete(rule)
    db.commit()
