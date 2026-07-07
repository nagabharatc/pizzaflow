from app.contexts.order.entities.order_item import OrderItem
from app.contexts.order.repositories.order_repository import OrderRepository
from app.contexts.order.schemas.order_schemas import (
    CustomerRequest,
    CustomerSummary,
    OrderItemRequest,
    OrderItemResponse,
    PendingOrderResponse,
)
from app.contexts.reference.repositories.base_repository import BaseRepository
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.repositories.topping_repository import ToppingRepository
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        menu_repository: MenuRepository,
        base_repository: BaseRepository,
        topping_repository: ToppingRepository,
    ):
        self._order_repo = order_repository
        self._menu_repo = menu_repository
        self._base_repo = base_repository
        self._topping_repo = topping_repository

    def submit_order(
        self,
        customer_data: CustomerRequest,
        items: list[OrderItemRequest],
    ) -> PendingOrderResponse:
        resolved_items = self._validate_and_resolve_items(items)
        customer = self._find_or_create_customer(customer_data)
        order = self._order_repo.save_order(customer.id)
        order_items = self._build_and_save_order_items(order.id, resolved_items)

        return PendingOrderResponse(
            order_id=order.id,
            status=order.status,
            customer=CustomerSummary(name=customer.name, phone_number=customer.phone_number),
            items=[
                OrderItemResponse(
                    menu_item_id=oi.menu_item_id,
                    name=resolved["menu_item"].name,
                    base_selected=oi.base_selected,
                    toppings_selected=oi.toppings_selected,
                    quantity=oi.quantity,
                    unit_price=oi.unit_price,
                )
                for oi, resolved in zip(order_items, resolved_items)
            ],
            created_at=order.created_at,
        )

    def _validate_and_resolve_items(self, items: list[OrderItemRequest]) -> list[dict]:
        resolved = []
        for item in items:
            menu_item = self._menu_repo.get_by_id(item.menu_item_id)

            if menu_item is None:
                raise ResourceNotFoundError(
                    message=f"Menu item {item.menu_item_id} does not exist",
                    detail=f"menu_item_id: {item.menu_item_id}",
                )
            if not menu_item.is_available:
                raise BusinessRuleViolationError(
                    message=f"'{menu_item.name}' is not currently available",
                    detail=f"menu_item_id: {item.menu_item_id}",
                )

            base = self._base_repo.get_by_name(item.base_selected)
            if base is None:
                raise BusinessRuleViolationError(
                    message=f"Base '{item.base_selected}' is not available for '{menu_item.name}'",
                    detail=f"base_selected: {item.base_selected}",
                )

            toppings = []
            for topping_name in item.toppings_selected:
                topping = self._topping_repo.get_by_name(topping_name)
                if topping is None:
                    raise BusinessRuleViolationError(
                        message=f"Topping '{topping_name}' is not available for '{menu_item.name}'",
                        detail=f"toppings_selected: {topping_name}",
                    )
                toppings.append(topping)

            unit_price = menu_item.price + base.price + sum(t.price for t in toppings)
            resolved.append({
                "request": item,
                "menu_item": menu_item,
                "unit_price": unit_price,
            })

        return resolved

    def _find_or_create_customer(self, customer_data: CustomerRequest):
        customer = self._order_repo.find_customer_by_phone(customer_data.phone_number)
        if customer is None:
            customer = self._order_repo.save_customer(customer_data)
        return customer

    def _build_and_save_order_items(self, order_id: int, resolved_items: list[dict]) -> list[OrderItem]:
        order_items = [
            OrderItem(
                order_id=order_id,
                menu_item_id=resolved["request"].menu_item_id,
                base_selected=resolved["request"].base_selected,
                toppings_selected=resolved["request"].toppings_selected,
                quantity=resolved["request"].quantity,
                unit_price=resolved["unit_price"],
            )
            for resolved in resolved_items
        ]
        return self._order_repo.save_order_items(order_items)
