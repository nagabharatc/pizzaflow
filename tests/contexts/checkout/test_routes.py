import pytest

from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.reference.entities.menu_item import MenuItem


@pytest.fixture
def pending_order(db_session) -> Order:
    menu_item = MenuItem(
        code="P1", name="Margherita", category="Pizza",
        price=299.0, is_available=True,
    )
    db_session.add(menu_item)
    db_session.flush()

    customer = Customer(name="Rajan", phone_number="9999999999")
    db_session.add(customer)
    db_session.flush()

    order = Order(customer_id=customer.id, status="pending")
    db_session.add(order)
    db_session.flush()

    item = OrderItem(
        order_id=order.id, menu_item_id=menu_item.id,
        base_selected="Thin Crust", toppings_selected=[],
        quantity=2, unit_price=299.0,
    )
    db_session.add(item)
    db_session.commit()

    return order


def test_complete_checkout_returns_200(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "card",
    })

    assert response.status_code == 200


def test_complete_checkout_response_status_is_paid(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "card",
    })

    assert response.json()["status"] == "paid"


def test_complete_checkout_response_includes_bill(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "cash",
    })
    bill = response.json()["bill"]

    assert "subtotal" in bill
    assert "gst_rate" in bill
    assert "gst_amount" in bill
    assert "total_amount" in bill


def test_complete_checkout_gst_is_18_percent(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "cash",
    })
    bill = response.json()["bill"]

    assert bill["gst_rate"] == 18.0
    assert bill["subtotal"] == 598.0        # 2 × 299.0
    assert bill["gst_amount"] == 107.64     # 598 × 18%
    assert bill["total_amount"] == 705.64   # 598 + 107.64


def test_complete_checkout_payment_method_recorded(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "upi",
    })

    assert response.json()["payment_method"] == "upi"


def test_complete_checkout_nonexistent_order_returns_404(client):
    response = client.post("/checkout", json={
        "pending_order_id": 99999,
        "payment_method": "cash",
    })

    assert response.status_code == 404


def test_complete_checkout_already_paid_order_returns_404(client, pending_order, db_session):
    client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "card",
    })
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "card",
    })

    assert response.status_code == 404


def test_complete_checkout_invalid_payment_method_returns_422(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "bitcoin",
    })

    assert response.status_code == 422


def test_complete_checkout_response_includes_paid_at(client, pending_order):
    response = client.post("/checkout", json={
        "pending_order_id": pending_order.id,
        "payment_method": "card",
    })

    assert "paid_at" in response.json()
    assert response.json()["paid_at"] is not None
