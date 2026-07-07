import pytest

from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.reference.entities.menu_item import MenuItem


@pytest.fixture
def paid_order(db_session) -> Order:
    menu_item = MenuItem(
        code="P1", name="Margherita", category="Pizza",
        price=299.0, is_available=True,
    )
    db_session.add(menu_item)
    db_session.flush()

    customer = Customer(name="Rajan", phone_number="9999999999")
    db_session.add(customer)
    db_session.flush()

    order = Order(customer_id=customer.id, status="paid")
    db_session.add(order)
    db_session.flush()

    item = OrderItem(
        order_id=order.id, menu_item_id=menu_item.id,
        base_selected="Thin Crust", toppings_selected=[],
        quantity=2, unit_price=299.0,
    )
    db_session.add(item)
    db_session.flush()

    bill = Bill(
        order_id=order.id, subtotal=598.0, gst_rate=18.0,
        gst_amount=107.64, total_amount=705.64,
    )
    db_session.add(bill)
    db_session.flush()

    payment = Payment(
        order_id=order.id, bill_id=bill.id,
        payment_method="card", amount_paid=705.64,
    )
    db_session.add(payment)
    db_session.commit()

    return order


def test_get_analytics_returns_200(client):
    response = client.get("/analytics")

    assert response.status_code == 200


def test_get_analytics_response_has_intelligence_key(client):
    response = client.get("/analytics")

    assert "intelligence" in response.json()


def test_get_analytics_intelligence_has_all_metric_sections(client):
    response = client.get("/analytics")
    intelligence = response.json()["intelligence"]

    assert "revenue" in intelligence
    assert "sales" in intelligence
    assert "customers" in intelligence
    assert "products" in intelligence
    assert "payments" in intelligence
    assert "growth" in intelligence


def test_get_analytics_revenue_fields_present(client):
    response = client.get("/analytics")
    revenue = response.json()["intelligence"]["revenue"]

    assert "total_revenue" in revenue
    assert "total_gst_collected" in revenue
    assert "average_order_value" in revenue


def test_get_analytics_with_paid_order_shows_correct_revenue(client, paid_order):
    response = client.get("/analytics")
    revenue = response.json()["intelligence"]["revenue"]

    assert revenue["total_revenue"] == 705.64
    assert revenue["total_gst_collected"] == 107.64


def test_get_analytics_filters_applied_echoed(client):
    response = client.get("/analytics?payment_method=card")
    filters = response.json()["filters_applied"]

    assert filters["payment_method"] == "card"


def test_get_analytics_no_data_returns_zeroed_metrics(client):
    response = client.get("/analytics")
    revenue = response.json()["intelligence"]["revenue"]

    assert revenue["total_revenue"] == 0.0
    assert revenue["total_gst_collected"] == 0.0


def test_get_analytics_filters_by_payment_method(client, paid_order):
    response_card = client.get("/analytics?payment_method=card")
    response_cash = client.get("/analytics?payment_method=cash")

    assert response_card.json()["intelligence"]["revenue"]["total_revenue"] == 705.64
    assert response_cash.json()["intelligence"]["revenue"]["total_revenue"] == 0.0
