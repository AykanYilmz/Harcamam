import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.categories import RuleRead
from app.schemas.transactions import (
    BulkCategoryResult,
    BulkCategoryUpdate,
    TransactionCategoryUpdate,
    TransactionCorrectionResult,
    TransactionFilters,
    TransactionPage,
    TransactionRead,
    UncategorizedMerchantRead,
    UncategorizedReport,
)
from app.services.categories import CategoryNotFoundError, InvalidKeywordError
from app.services.transactions import (
    TransactionNotFoundError,
    bulk_set_category,
    correct_category,
    list_transactions,
    uncategorized_merchants,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

CATEGORY_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found")


@router.get("", response_model=TransactionPage)
def get_transactions(
    filters: Annotated[TransactionFilters, Query()], current_user: CurrentUser, db: DbSession
) -> TransactionPage:
    items, total, pages = list_transactions(db, current_user, filters)
    return TransactionPage(
        items=[TransactionRead.model_validate(item) for item in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        pages=pages,
    )


@router.get("/uncategorized", response_model=UncategorizedReport)
def get_uncategorized(current_user: CurrentUser, db: DbSession) -> UncategorizedReport:
    merchants = uncategorized_merchants(db, current_user)
    return UncategorizedReport(
        transaction_count=sum(len(merchant.transactions) for merchant in merchants),
        merchants=[
            UncategorizedMerchantRead(
                name=merchant.name,
                keyword=merchant.name,
                amount=merchant.amount,
                transactions=[TransactionRead.model_validate(t) for t in merchant.transactions],
            )
            for merchant in merchants
        ],
    )


# Declared before /{transaction_id} so "bulk" isn't parsed as a transaction id.
@router.patch("/bulk", response_model=BulkCategoryResult)
def bulk_update_category(
    payload: BulkCategoryUpdate, current_user: CurrentUser, db: DbSession
) -> BulkCategoryResult:
    try:
        updated = bulk_set_category(db, current_user, payload.transaction_ids, payload.category_id)
    except CategoryNotFoundError as exc:
        raise CATEGORY_NOT_FOUND from exc
    except TransactionNotFoundError as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="One or more transactions were not found"
        ) from exc
    return BulkCategoryResult(updated=updated)


@router.patch("/{transaction_id}", response_model=TransactionCorrectionResult)
def update_category(
    transaction_id: uuid.UUID,
    payload: TransactionCategoryUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> TransactionCorrectionResult:
    try:
        transaction, rule, updated = correct_category(
            db, current_user, transaction_id, payload.category_id, payload.rule_keyword
        )
    except TransactionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Transaction not found") from exc
    except CategoryNotFoundError as exc:
        raise CATEGORY_NOT_FOUND from exc
    except InvalidKeywordError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The keyword must contain a letter or digit",
        ) from exc

    return TransactionCorrectionResult(
        transaction=TransactionRead.model_validate(transaction),
        rule=RuleRead.model_validate(rule) if rule else None,
        updated_transactions=updated,
    )
