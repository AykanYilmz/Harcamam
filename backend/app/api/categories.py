import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models import Category, CategoryRule
from app.schemas.categories import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    RuleCreate,
    RuleRead,
    RuleSaveResult,
)
from app.services import categories as service

router = APIRouter(tags=["categories"])

CATEGORY_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")
DEFAULT_READ_ONLY = HTTPException(
    status.HTTP_403_FORBIDDEN, detail="Default categories cannot be changed"
)
NAME_TAKEN = HTTPException(status.HTTP_409_CONFLICT, detail="A category with this name exists")


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(current_user: CurrentUser, db: DbSession) -> list[Category]:
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, current_user: CurrentUser, db: DbSession) -> Category:
    try:
        return service.create_category(db, current_user, payload.name, payload.color, payload.icon)
    except service.CategoryNameTakenError as exc:
        raise NAME_TAKEN from exc


@router.patch("/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: uuid.UUID, payload: CategoryUpdate, current_user: CurrentUser, db: DbSession
) -> Category:
    try:
        return service.update_category(
            db, current_user, category_id, **payload.model_dump(exclude_unset=True)
        )
    except service.CategoryNotFoundError as exc:
        raise CATEGORY_NOT_FOUND from exc
    except service.DefaultCategoryReadOnlyError as exc:
        raise DEFAULT_READ_ONLY from exc
    except service.CategoryNameTakenError as exc:
        raise NAME_TAKEN from exc


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    try:
        service.delete_category(db, current_user, category_id)
    except service.CategoryNotFoundError as exc:
        raise CATEGORY_NOT_FOUND from exc
    except service.DefaultCategoryReadOnlyError as exc:
        raise DEFAULT_READ_ONLY from exc


@router.get("/category-rules", response_model=list[RuleRead])
def list_rules(current_user: CurrentUser, db: DbSession) -> list[CategoryRule]:
    return service.list_rules(db, current_user)


@router.post("/category-rules", response_model=RuleSaveResult, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleCreate, current_user: CurrentUser, db: DbSession) -> RuleSaveResult:
    try:
        rule, updated = service.save_rule(
            db, current_user, payload.keyword, payload.category_id, payload.apply_to_existing
        )
    except service.InvalidKeywordError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The keyword must contain a letter or digit",
        ) from exc
    except service.CategoryNotFoundError as exc:
        raise CATEGORY_NOT_FOUND from exc
    db.commit()
    return RuleSaveResult(rule=RuleRead.model_validate(rule), updated_transactions=updated)


@router.delete("/category-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: uuid.UUID, current_user: CurrentUser, db: DbSession) -> None:
    try:
        service.delete_rule(db, current_user, rule_id)
    except service.RuleNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Rule not found") from exc
