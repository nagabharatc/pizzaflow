from app.contexts.checkout.repositories.checkout_repository import CheckoutRepository
from app.contexts.checkout.repositories.discount_settings_repository import DiscountSettingsRepository
from app.contexts.checkout.schemas.checkout_schemas import (
    BillResponse,
    CheckoutItemResponse,
    CompleteCheckoutResponse,
)
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError

GST_RATE = 18.0
DISCOUNT_RATE = 10.0


class CheckoutService:
    def __init__(
        self,
        repository: CheckoutRepository,
        discount_settings_repository: DiscountSettingsRepository,
        menu_repository: MenuRepository,
    ):
        self._repo = repository
        self._discount_settings_repo = discount_settings_repository
        self._menu_repo = menu_repository

    def complete_checkout(
        self, pending_order_id: int, payment_method: str
    ) -> CompleteCheckoutResponse:
        order = self._repo.get_pending_order(pending_order_id)
        if order is None:
            raise ResourceNotFoundError(
                message=f"No pending order found with ID {pending_order_id}",
                detail=f"pending_order_id: {pending_order_id}",
            )

        order_items = self._repo.get_order_items(pending_order_id)
        if not order_items:
            raise BusinessRuleViolationError(
                message="Order has no items and cannot be checked out",
                detail=f"order_id: {pending_order_id}",
            )

        subtotal = sum(item.unit_price * item.quantity for item in order_items)
        total_quantity = sum(item.quantity for item in order_items)
        threshold = self._discount_settings_repo.get_quantity_threshold()

        discount_rate = DISCOUNT_RATE if total_quantity >= threshold else 0.0
        discount_amount = round(subtotal * discount_rate / 100, 2)
        taxable_amount = round(subtotal - discount_amount, 2)
        gst_amount = round(taxable_amount * GST_RATE / 100, 2)
        total_amount = round(taxable_amount + gst_amount, 2)

        order, bill, payment = self._repo.complete_transaction(
            order=order,
            subtotal=subtotal,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            gst_rate=GST_RATE,
            gst_amount=gst_amount,
            total_amount=total_amount,
            payment_method=payment_method,
        )

        items = [
            CheckoutItemResponse(
                name=self._menu_repo.get_by_id(item.menu_item_id).name,
                base_selected=item.base_selected,
                toppings_selected=item.toppings_selected,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=round(item.unit_price * item.quantity, 2),
            )
            for item in order_items
        ]

        return CompleteCheckoutResponse(
            order_id=order.id,
            status=order.status,
            items=items,
            bill=BillResponse(
                subtotal=bill.subtotal,
                discount_rate=bill.discount_rate,
                discount_amount=bill.discount_amount,
                gst_rate=bill.gst_rate,
                gst_amount=bill.gst_amount,
                total_amount=bill.total_amount,
            ),
            payment_method=payment.payment_method,
            paid_at=payment.created_at,
        )
