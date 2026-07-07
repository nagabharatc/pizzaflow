from unittest.mock import MagicMock

import pytest

from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.order.repositories.order_repository import OrderRepository
from app.contexts.order.schemas.order_schemas import (
    CustomerRequest,
    OrderItemRequest,
    PendingOrderResponse,
)
from app.contexts.order.service import OrderService
from app.contexts.reference.entities.base import Base
from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.entities.topping import Topping
from app.contexts.reference.repositories.base_repository import BaseRepository
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.repositories.topping_repository import ToppingRepository
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError
from datetime import datetime


@pytest.fixture
def mock_order_repo() -> OrderRepository:
    return MagicMock(spec=OrderRepository)


@pytest.fixture
def mock_menu_repo() -> MenuRepository:
    return MagicMock(spec=MenuRepository)


@pytest.fixture
def mock_base_repo() -> BaseRepository:
    return MagicMock(spec=BaseRepository)


@pytest.fixture
def mock_topping_repo() -> ToppingRepository:
    return MagicMock(spec=ToppingRepository)


@pytest.fixture
def service(mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo) -> OrderService:
    return OrderService(
        order_repository=mock_order_repo,
        menu_repository=mock_menu_repo,
        base_repository=mock_base_repo,
        topping_repository=mock_topping_repo,
    )


@pytest.fixture
def available_menu_item() -> MenuItem:
    return MenuItem(id=1, code="P1", name="Margherita", category="Pizza", price=299.0, is_available=True)


@pytest.fixture
def thin_crust_base() -> Base:
    return Base(id=1, code="B1", name="Thin Crust", price=149.0)


@pytest.fixture
def mozzarella_topping() -> Topping:
    return Topping(id=1, code="T1", name="Mozzarella", price=69.0)


@pytest.fixture
def valid_customer_request() -> CustomerRequest:
    return CustomerRequest(name="Rajan", phone_number="9999999999")


@pytest.fixture
def valid_item_request() -> OrderItemRequest:
    return OrderItemRequest(
        menu_item_id=1,
        base_selected="Thin Crust",
        toppings_selected=["Mozzarella"],
        quantity=2,
    )


def _setup_happy_path(mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
                       menu_item, base, toppings_by_name, customer_request):
    mock_menu_repo.get_by_id.return_value = menu_item
    mock_base_repo.get_by_name.return_value = base
    mock_topping_repo.get_by_name.side_effect = lambda name: toppings_by_name.get(name)
    mock_order_repo.find_customer_by_phone.return_value = None
    mock_order_repo.save_customer.return_value = Customer(
        id=1, name=customer_request.name, phone_number=customer_request.phone_number,
        created_at=datetime.utcnow(),
    )
    mock_order_repo.save_order.return_value = Order(
        id=10, customer_id=1, status="pending", created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_submit_order_returns_pending_order_response(
    service, mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
    available_menu_item, thin_crust_base, mozzarella_topping, valid_customer_request, valid_item_request
):
    _setup_happy_path(
        mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
        available_menu_item, thin_crust_base, {"Mozzarella": mozzarella_topping}, valid_customer_request,
    )
    mock_order_repo.save_order_items.return_value = [
        OrderItem(
            id=1, order_id=10, menu_item_id=1,
            base_selected="Thin Crust", toppings_selected=["Mozzarella"],
            quantity=2, unit_price=517.0,
        )
    ]

    result = service.submit_order(valid_customer_request, [valid_item_request])

    assert isinstance(result, PendingOrderResponse)
    assert result.order_id == 10
    assert result.status == "pending"
    assert result.customer.name == "Rajan"
    assert len(result.items) == 1
    assert result.items[0].name == "Margherita"


def test_submit_order_unit_price_combines_pizza_base_and_toppings(
    service, mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
    available_menu_item, thin_crust_base, mozzarella_topping, valid_customer_request, valid_item_request
):
    _setup_happy_path(
        mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
        available_menu_item, thin_crust_base, {"Mozzarella": mozzarella_topping}, valid_customer_request,
    )
    mock_order_repo.save_order_items.return_value = [
        OrderItem(
            id=1, order_id=10, menu_item_id=1,
            base_selected="Thin Crust", toppings_selected=["Mozzarella"],
            quantity=2, unit_price=517.0,
        )
    ]

    service.submit_order(valid_customer_request, [valid_item_request])

    saved_items = mock_order_repo.save_order_items.call_args[0][0]
    assert saved_items[0].unit_price == 299.0 + 149.0 + 69.0


def test_submit_order_status_is_always_pending(
    service, mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
    available_menu_item, thin_crust_base, mozzarella_topping, valid_customer_request, valid_item_request
):
    _setup_happy_path(
        mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
        available_menu_item, thin_crust_base, {"Mozzarella": mozzarella_topping}, valid_customer_request,
    )
    mock_order_repo.save_order_items.return_value = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=["Mozzarella"], quantity=2, unit_price=517.0),
    ]

    result = service.submit_order(valid_customer_request, [valid_item_request])

    assert result.status == "pending"
    saved_order_call = mock_order_repo.save_order.call_args
    assert saved_order_call is not None


def test_submit_order_reuses_existing_customer(
    service, mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
    available_menu_item, thin_crust_base, mozzarella_topping, valid_customer_request, valid_item_request
):
    existing_customer = Customer(
        id=5, name="Rajan", phone_number="9999999999", created_at=datetime.utcnow()
    )
    mock_menu_repo.get_by_id.return_value = available_menu_item
    mock_base_repo.get_by_name.return_value = thin_crust_base
    mock_topping_repo.get_by_name.return_value = mozzarella_topping
    mock_order_repo.find_customer_by_phone.return_value = existing_customer
    mock_order_repo.save_order.return_value = Order(
        id=10, customer_id=5, status="pending", created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    mock_order_repo.save_order_items.return_value = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=["Mozzarella"], quantity=2, unit_price=517.0),
    ]

    service.submit_order(valid_customer_request, [valid_item_request])

    mock_order_repo.save_customer.assert_not_called()
    mock_order_repo.save_order.assert_called_with(existing_customer.id)


def test_submit_order_raises_when_menu_item_not_found(
    service, mock_menu_repo, valid_customer_request, valid_item_request
):
    mock_menu_repo.get_by_id.return_value = None

    with pytest.raises(ResourceNotFoundError) as exc:
        service.submit_order(valid_customer_request, [valid_item_request])

    assert "1" in exc.value.message


def test_submit_order_raises_when_menu_item_unavailable(
    service, mock_menu_repo, available_menu_item, valid_customer_request, valid_item_request
):
    available_menu_item.is_available = False
    mock_menu_repo.get_by_id.return_value = available_menu_item

    with pytest.raises(BusinessRuleViolationError):
        service.submit_order(valid_customer_request, [valid_item_request])


def test_submit_order_raises_when_base_not_available(
    service, mock_menu_repo, mock_base_repo, available_menu_item, valid_customer_request
):
    mock_menu_repo.get_by_id.return_value = available_menu_item
    mock_base_repo.get_by_name.return_value = None
    item_with_invalid_base = OrderItemRequest(
        menu_item_id=1, base_selected="Stuffed Crust", toppings_selected=[], quantity=1
    )

    with pytest.raises(BusinessRuleViolationError) as exc:
        service.submit_order(valid_customer_request, [item_with_invalid_base])

    assert "Stuffed Crust" in exc.value.message


def test_submit_order_raises_when_topping_not_available(
    service, mock_menu_repo, mock_base_repo, mock_topping_repo,
    available_menu_item, thin_crust_base, valid_customer_request
):
    mock_menu_repo.get_by_id.return_value = available_menu_item
    mock_base_repo.get_by_name.return_value = thin_crust_base
    mock_topping_repo.get_by_name.return_value = None
    item_with_invalid_topping = OrderItemRequest(
        menu_item_id=1, base_selected="Thin Crust",
        toppings_selected=["Bacon"],
        quantity=1,
    )

    with pytest.raises(BusinessRuleViolationError) as exc:
        service.submit_order(valid_customer_request, [item_with_invalid_topping])

    assert "Bacon" in exc.value.message


def test_submit_order_accepts_empty_toppings(
    service, mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
    available_menu_item, thin_crust_base, valid_customer_request
):
    _setup_happy_path(
        mock_order_repo, mock_menu_repo, mock_base_repo, mock_topping_repo,
        available_menu_item, thin_crust_base, {}, valid_customer_request,
    )
    mock_order_repo.save_order_items.return_value = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=1, unit_price=448.0),
    ]
    item_no_toppings = OrderItemRequest(
        menu_item_id=1, base_selected="Thin Crust", toppings_selected=[], quantity=1
    )

    result = service.submit_order(valid_customer_request, [item_no_toppings])

    assert result.items[0].toppings_selected == []
