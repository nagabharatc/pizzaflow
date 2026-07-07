from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.contexts.checkout.repositories.checkout_repository import CheckoutRepository
from app.contexts.checkout.repositories.discount_settings_repository import DiscountSettingsRepository
from app.contexts.checkout.schemas.checkout_schemas import (
    CompleteCheckoutRequest,
    CompleteCheckoutResponse,
)
from app.contexts.checkout.service import CheckoutService
from app.contexts.reference.repositories.menu_repository import MenuRepository


router = APIRouter()


def get_checkout_service(db: Session = Depends(get_db)) -> CheckoutService:
    return CheckoutService(
        repository=CheckoutRepository(db),
        discount_settings_repository=DiscountSettingsRepository(db),
        menu_repository=MenuRepository(db),
    )


@router.post("", response_model=CompleteCheckoutResponse)
def complete_checkout(
    request: CompleteCheckoutRequest,
    service: CheckoutService = Depends(get_checkout_service),
) -> CompleteCheckoutResponse:
    return service.complete_checkout(request.pending_order_id, request.payment_method)
