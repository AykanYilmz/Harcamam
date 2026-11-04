from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.subscriptions import (
    DismissedSubscriptionRead,
    SubscriptionKey,
    SubscriptionRead,
    SubscriptionReport,
)
from app.services import subscriptions as service
from app.services.reports import ZERO

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def to_read(subscription: service.Subscription) -> SubscriptionRead:
    return SubscriptionRead(
        key=subscription.key,
        name=subscription.name,
        category_id=subscription.category.id,
        category_name=subscription.category.name,
        color=subscription.category.color,
        icon=subscription.category.icon,
        amount=subscription.amount,
        yearly_amount=subscription.yearly_amount,
        previous_amount=subscription.previous_amount,
        charge_count=len(subscription.charges),
        first_charge=subscription.charges[0].date,
        last_charge=subscription.charges[-1].date,
        next_charge=subscription.next_charge,
        active=subscription.active,
    )


@router.get("", response_model=SubscriptionReport)
def list_subscriptions(current_user: CurrentUser, db: DbSession) -> SubscriptionReport:
    found = service.find_subscriptions(db, current_user)
    active = [subscription for subscription in found if subscription.active]
    monthly = sum((subscription.amount for subscription in active), ZERO)
    return SubscriptionReport(
        monthly_total=monthly,
        yearly_total=monthly * 12,
        subscriptions=[to_read(subscription) for subscription in found],
        dismissed=[
            DismissedSubscriptionRead(key=item.merchant_key, name=item.name)
            for item in service.dismissed(db, current_user)
        ],
    )


@router.post("/dismissed", status_code=status.HTTP_204_NO_CONTENT)
def dismiss(payload: SubscriptionKey, current_user: CurrentUser, db: DbSession) -> None:
    """Mark a detected payment as not a subscription."""
    try:
        service.dismiss(db, current_user, payload.key)
    except service.SubscriptionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Subscription not found") from exc


@router.delete("/dismissed/{key}", status_code=status.HTTP_204_NO_CONTENT)
def restore(key: str, current_user: CurrentUser, db: DbSession) -> None:
    """Show a dismissed payment again, if it is still detected."""
    service.restore(db, current_user, key)
