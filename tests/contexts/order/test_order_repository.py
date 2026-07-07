import pytest

from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.order.repositories.order_repository import OrderRepository
from app.contexts.order.schemas.order_schemas import CustomerRequest
from app.contexts.reference.entities.menu_item import MenuItem


@pytest.fixture
def repository(db_session) -> OrderRepository:
    return OrderRepository(db_session)


@pytest.fixture
def saved_menu_item(db_session) -> MenuItem:
    item = MenuItem(
        code="P1", name="Margherita", category="Pizza",
        price=299.0, is_available=True,
    )
    db_session.add(item)
    db_session.commit()
    return item


@pytest.fixture
def saved_customer(db_session) -> Customer:
    customer = Customer(name="Rajan", phone_number="9999999999")
    db_session.add(customer)
    db_session.commit()
    return customer


def test_find_customer_by_phone_returns_existing_customer(repository, saved_customer):
    result = repository.find_customer_by_phone("9999999999")

    assert result is not None
    assert result.name == "Rajan"
    assert result.id == saved_customer.id


def test_find_customer_by_phone_returns_none_for_unknown_number(repository):
    result = repository.find_customer_by_phone("0000000000")

    assert result is None


def test_save_customer_persists_and_returns_customer(repository, db_session):
    customer_data = CustomerRequest(name="Priya", phone_number="8888888888")

    result = repository.save_customer(customer_data)

    assert result.id is not None
    assert result.name == "Priya"
    assert result.phone_number == "8888888888"
    in_db = db_session.query(Customer).filter_by(phone_number="8888888888").first()
    assert in_db is not None


def test_save_order_creates_order_with_pending_status(repository, saved_customer):
    result = repository.save_order(saved_customer.id)

    assert result.id is not None
    assert result.customer_id == saved_customer.id
    assert result.status == "pending"


def test_save_order_never_creates_paid_order(repository, saved_customer):
    result = repository.save_order(saved_customer.id)

    assert result.status == "pending"
    assert result.status != "paid"


def test_save_order_items_persists_all_items(repository, saved_customer, saved_menu_item, db_session):
    order = repository.save_order(saved_customer.id)
    items = [
        OrderItem(
            order_id=order.id, menu_item_id=saved_menu_item.id,
            base_selected="Thin Crust", toppings_selected=["Mozzarella"],
            quantity=2, unit_price=299.0,
        ),
        OrderItem(
            order_id=order.id, menu_item_id=saved_menu_item.id,
            base_selected="Thin Crust", toppings_selected=[],
            quantity=1, unit_price=299.0,
        ),
    ]

    result = repository.save_order_items(items)

    assert len(result) == 2
    assert all(item.id is not None for item in result)
    in_db = db_session.query(OrderItem).filter_by(order_id=order.id).all()
    assert len(in_db) == 2


def test_save_order_items_captures_unit_price(repository, saved_customer, saved_menu_item):
    order = repository.save_order(saved_customer.id)
    items = [
        OrderItem(
            order_id=order.id, menu_item_id=saved_menu_item.id,
            base_selected="Thin Crust", toppings_selected=[],
            quantity=1, unit_price=499.0,
        ),
    ]

    result = repository.save_order_items(items)

    assert result[0].unit_price == 499.0
