import pytest
from datetime import datetime

from app.contexts.analytics.repositories.analytics_repository import AnalyticsRepository
from app.contexts.analytics.schemas.analytics_schemas import AnalyticsRequest
from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.reference.entities.menu_item import MenuItem


@pytest.fixture
def repository(db_session) -> AnalyticsRepository:
    return AnalyticsRepository(db_session)


@pytest.fixture
def seeded_data(db_session) -> dict:
    menu_item = MenuItem(
        code="P1", name="Margherita", category="Pizza",
        price=299.0, is_available=True,
    )
    db_session.add(menu_item)
    db_session.flush()

    customer1 = Customer(name="Rajan", phone_number="9999999999")
    customer2 = Customer(name="Priya", phone_number="8888888888")
    db_session.add_all([customer1, customer2])
    db_session.flush()

    order1 = Order(customer_id=customer1.id, status="paid")
    order2 = Order(customer_id=customer2.id, status="pending")
    db_session.add_all([order1, order2])
    db_session.flush()

    item1 = OrderItem(order_id=order1.id, menu_item_id=menu_item.id, base_selected="Thin Crust", toppings_selected=[], quantity=2, unit_price=299.0)
    item2 = OrderItem(order_id=order2.id, menu_item_id=menu_item.id, base_selected="Thin Crust", toppings_selected=[], quantity=1, unit_price=299.0)
    db_session.add_all([item1, item2])
    db_session.flush()

    bill1 = Bill(order_id=order1.id, subtotal=598.0, gst_rate=18.0, gst_amount=107.64, total_amount=705.64)
    db_session.add(bill1)
    db_session.flush()

    payment1 = Payment(order_id=order1.id, bill_id=bill1.id, payment_method="card", amount_paid=705.64)
    db_session.add(payment1)
    db_session.commit()

    return {
        "menu_item": menu_item,
        "customer1": customer1,
        "customer2": customer2,
        "order1": order1,
        "order2": order2,
        "bill1": bill1,
        "payment1": payment1,
    }


def test_get_paid_orders_returns_only_paid_orders(repository, seeded_data):
    result = repository.get_paid_orders(AnalyticsRequest())

    assert len(result) == 1
    assert result[0].id == seeded_data["order1"].id
    assert result[0].status == "paid"


def test_get_paid_orders_returns_empty_when_no_paid_orders(repository):
    result = repository.get_paid_orders(AnalyticsRequest())

    assert result == []


def test_get_paid_orders_filters_by_payment_method(repository, seeded_data):
    result_card = repository.get_paid_orders(AnalyticsRequest(payment_method="card"))
    result_cash = repository.get_paid_orders(AnalyticsRequest(payment_method="cash"))

    assert len(result_card) == 1
    assert len(result_cash) == 0


def test_get_paid_orders_filters_by_customer_id(repository, seeded_data):
    customer1_id = seeded_data["customer1"].id
    result = repository.get_paid_orders(AnalyticsRequest(customer_id=customer1_id))

    assert len(result) == 1
    assert result[0].customer_id == customer1_id


def test_get_order_items_returns_items_for_given_order_ids(repository, seeded_data):
    order_id = seeded_data["order1"].id
    result = repository.get_order_items([order_id])

    assert len(result) == 1
    assert result[0].order_id == order_id


def test_get_order_items_returns_empty_for_empty_list(repository, seeded_data):
    result = repository.get_order_items([])

    assert result == []


def test_get_bills_returns_bills_for_given_order_ids(repository, seeded_data):
    order_id = seeded_data["order1"].id
    result = repository.get_bills([order_id])

    assert len(result) == 1
    assert result[0].order_id == order_id
    assert result[0].total_amount == 705.64


def test_get_bills_returns_empty_for_empty_list(repository, seeded_data):
    result = repository.get_bills([])

    assert result == []


def test_get_customers_returns_customers_for_given_ids(repository, seeded_data):
    customer_id = seeded_data["customer1"].id
    result = repository.get_customers([customer_id])

    assert len(result) == 1
    assert result[0].id == customer_id


def test_get_payments_returns_payments_for_given_order_ids(repository, seeded_data):
    order_id = seeded_data["order1"].id
    result = repository.get_payments([order_id])

    assert len(result) == 1
    assert result[0].payment_method == "card"
    assert result[0].amount_paid == 705.64
