from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.checkout.repositories.checkout_repository import CheckoutRepository
from app.contexts.checkout.repositories.discount_settings_repository import DiscountSettingsRepository
from app.contexts.checkout.schemas.checkout_schemas import CompleteCheckoutResponse
from app.contexts.checkout.service import CheckoutService, DISCOUNT_RATE, GST_RATE
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.shared.exceptions import BusinessRuleViolationError, ResourceNotFoundError

_MENU_ITEMS_BY_ID = {
    1: MenuItem(id=1, code="P1", name="Margherita", category="Pizza", price=299.0, is_available=True),
    2: MenuItem(id=2, code="P2", name="Farmhouse", category="Pizza", price=50.0, is_available=True),
}


@pytest.fixture
def mock_repo() -> CheckoutRepository:
    return MagicMock(spec=CheckoutRepository)


@pytest.fixture
def mock_discount_repo() -> DiscountSettingsRepository:
    repo = MagicMock(spec=DiscountSettingsRepository)
    repo.get_quantity_threshold.return_value = 5
    return repo


@pytest.fixture
def mock_menu_repo() -> MenuRepository:
    repo = MagicMock(spec=MenuRepository)
    repo.get_by_id.side_effect = lambda menu_item_id: _MENU_ITEMS_BY_ID.get(menu_item_id)
    return repo


@pytest.fixture
def service(mock_repo, mock_discount_repo, mock_menu_repo) -> CheckoutService:
    return CheckoutService(
        repository=mock_repo,
        discount_settings_repository=mock_discount_repo,
        menu_repository=mock_menu_repo,
    )


@pytest.fixture
def pending_order() -> Order:
    return Order(id=10, customer_id=1, status="pending", created_at=datetime.utcnow(), updated_at=datetime.utcnow())


@pytest.fixture
def order_items() -> list[OrderItem]:
    return [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=2, unit_price=299.0),
    ]


@pytest.fixture
def completed_bill() -> Bill:
    return Bill(id=1, order_id=10, subtotal=598.0, discount_rate=0.0, discount_amount=0.0,
                gst_rate=18.0, gst_amount=107.64, total_amount=705.64, created_at=datetime.utcnow())


@pytest.fixture
def completed_payment() -> Payment:
    return Payment(id=1, order_id=10, bill_id=1, payment_method="card",
                   amount_paid=705.64, created_at=datetime.utcnow())


def _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment):
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = order_items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)


def test_complete_checkout_returns_response(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    result = service.complete_checkout(10, "card")

    assert isinstance(result, CompleteCheckoutResponse)
    assert result.order_id == 10
    assert result.status == "paid"
    assert result.payment_method == "card"


def test_complete_checkout_calculates_gst_at_18_percent(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    service.complete_checkout(10, "card")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["gst_rate"] == 18.0
    assert call_kwargs["subtotal"] == 598.0
    assert call_kwargs["gst_amount"] == 107.64
    assert call_kwargs["total_amount"] == 705.64


def test_complete_checkout_captures_gst_rate_at_transaction_time(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    service.complete_checkout(10, "cash")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["gst_rate"] == GST_RATE


def test_complete_checkout_calculates_subtotal_from_unit_price_times_quantity(service, mock_repo, pending_order, completed_bill, completed_payment):
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=3, unit_price=399.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    service.complete_checkout(10, "upi")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["subtotal"] == 1197.0  # 3 × 399.0


def test_complete_checkout_raises_resource_not_found_for_unknown_order(service, mock_repo):
    mock_repo.get_pending_order.return_value = None

    with pytest.raises(ResourceNotFoundError) as exc:
        service.complete_checkout(99999, "cash")

    assert "99999" in exc.value.message


def test_complete_checkout_raises_when_order_has_no_items(service, mock_repo, pending_order):
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = []

    with pytest.raises(BusinessRuleViolationError):
        service.complete_checkout(10, "cash")


def test_complete_checkout_passes_payment_method_to_repository(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    service.complete_checkout(10, "upi")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["payment_method"] == "upi"


def test_complete_checkout_bill_fields_in_response(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    result = service.complete_checkout(10, "card")

    assert result.bill.subtotal == 598.0
    assert result.bill.discount_rate == 0.0
    assert result.bill.discount_amount == 0.0
    assert result.bill.gst_rate == 18.0
    assert result.bill.gst_amount == 107.64
    assert result.bill.total_amount == 705.64


def test_complete_checkout_response_includes_itemized_lines(service, mock_repo, pending_order, order_items, completed_bill, completed_payment):
    _setup_happy_path(mock_repo, pending_order, order_items, completed_bill, completed_payment)

    result = service.complete_checkout(10, "card")

    assert len(result.items) == 1
    line = result.items[0]
    assert line.name == "Margherita"
    assert line.base_selected == "Thin Crust"
    assert line.toppings_selected == []
    assert line.quantity == 2
    assert line.unit_price == 299.0
    assert line.line_total == 598.0


def test_complete_checkout_itemizes_multiple_lines_with_correct_totals(service, mock_repo, mock_discount_repo, pending_order, completed_bill, completed_payment):
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=["Extra Cheese"], quantity=3, unit_price=100.0),
        OrderItem(id=2, order_id=10, menu_item_id=2, base_selected="Thick Crust",
                  toppings_selected=[], quantity=2, unit_price=50.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    result = service.complete_checkout(10, "card")

    assert len(result.items) == 2
    assert result.items[0].name == "Margherita"
    assert result.items[0].toppings_selected == ["Extra Cheese"]
    assert result.items[0].line_total == 300.0
    assert result.items[1].name == "Farmhouse"
    assert result.items[1].line_total == 100.0


def test_complete_checkout_no_discount_below_threshold(service, mock_repo, mock_discount_repo, pending_order, completed_bill, completed_payment):
    # total quantity 4 < threshold 5
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=4, unit_price=100.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    service.complete_checkout(10, "card")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["subtotal"] == 400.0
    assert call_kwargs["discount_rate"] == 0.0
    assert call_kwargs["discount_amount"] == 0.0
    assert call_kwargs["gst_amount"] == 72.0  # 400 × 18%
    assert call_kwargs["total_amount"] == 472.0


def test_complete_checkout_applies_discount_at_threshold(service, mock_repo, mock_discount_repo, pending_order, completed_bill, completed_payment):
    # total quantity exactly 5 == threshold 5
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=5, unit_price=100.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    service.complete_checkout(10, "card")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["subtotal"] == 500.0
    assert call_kwargs["discount_rate"] == DISCOUNT_RATE
    assert call_kwargs["discount_amount"] == 50.0  # 10% of 500
    assert call_kwargs["gst_amount"] == 81.0  # (500 - 50) × 18%
    assert call_kwargs["total_amount"] == 531.0  # 450 + 81


def test_complete_checkout_applies_discount_across_multiple_items(service, mock_repo, mock_discount_repo, pending_order, completed_bill, completed_payment):
    # 3 + 2 = 5 total quantity across two different line items
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=3, unit_price=100.0),
        OrderItem(id=2, order_id=10, menu_item_id=2, base_selected="Thick Crust",
                  toppings_selected=[], quantity=2, unit_price=50.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    service.complete_checkout(10, "card")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["subtotal"] == 400.0  # 300 + 100
    assert call_kwargs["discount_rate"] == DISCOUNT_RATE
    assert call_kwargs["discount_amount"] == 40.0


def test_complete_checkout_reads_threshold_from_repository(service, mock_repo, mock_discount_repo, pending_order, completed_bill, completed_payment):
    mock_discount_repo.get_quantity_threshold.return_value = 10  # raise the bar
    items = [
        OrderItem(id=1, order_id=10, menu_item_id=1, base_selected="Thin Crust",
                  toppings_selected=[], quantity=5, unit_price=100.0),
    ]
    paid_order = Order(id=10, customer_id=1, status="paid",
                       created_at=pending_order.created_at, updated_at=datetime.utcnow())
    mock_repo.get_pending_order.return_value = pending_order
    mock_repo.get_order_items.return_value = items
    mock_repo.complete_transaction.return_value = (paid_order, completed_bill, completed_payment)

    service.complete_checkout(10, "card")

    call_kwargs = mock_repo.complete_transaction.call_args.kwargs
    assert call_kwargs["discount_rate"] == 0.0  # quantity 5 < raised threshold 10
    mock_discount_repo.get_quantity_threshold.assert_called_once()
