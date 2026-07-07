import pytest

from app.contexts.reference.entities.base import Base
from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.entities.topping import Topping


@pytest.fixture
def menu_item(db_session) -> MenuItem:
    item = MenuItem(code="P1", name="Margherita", category="Pizza", price=299.0, is_available=True)
    db_session.add(item)
    db_session.add(Base(code="B1", name="Thin Crust", price=149.0))
    db_session.add(Topping(code="T1", name="Mozzarella", price=69.0))
    db_session.commit()
    return item


@pytest.fixture
def valid_payload(menu_item) -> dict:
    return {
        "customer": {"name": "Rajan", "phone_number": "9999999999"},
        "items": [
            {
                "menu_item_id": menu_item.id,
                "base_selected": "Thin Crust",
                "toppings_selected": ["Mozzarella"],
                "quantity": 2,
            }
        ],
    }


def test_submit_order_returns_201(client, valid_payload):
    response = client.post("/orders", json=valid_payload)

    assert response.status_code == 201


def test_submit_order_response_has_pending_status(client, valid_payload):
    response = client.post("/orders", json=valid_payload)

    assert response.json()["status"] == "pending"


def test_submit_order_response_includes_order_id(client, valid_payload):
    response = client.post("/orders", json=valid_payload)

    body = response.json()
    assert "order_id" in body
    assert isinstance(body["order_id"], int)


def test_submit_order_response_includes_customer(client, valid_payload):
    response = client.post("/orders", json=valid_payload)

    customer = response.json()["customer"]
    assert customer["name"] == "Rajan"
    assert customer["phone_number"] == "9999999999"


def test_submit_order_response_includes_items_with_combined_price(client, valid_payload, menu_item):
    response = client.post("/orders", json=valid_payload)

    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Margherita"
    assert items[0]["unit_price"] == menu_item.price + 149.0 + 69.0
    assert items[0]["quantity"] == 2


def test_submit_order_reuses_returning_customer(client, valid_payload):
    client.post("/orders", json=valid_payload)
    response = client.post("/orders", json=valid_payload)

    assert response.status_code == 201


def test_submit_order_missing_customer_name_returns_422(client, menu_item):
    payload = {
        "customer": {"phone_number": "9999999999"},
        "items": [{"menu_item_id": menu_item.id, "base_selected": "Thin Crust", "quantity": 1}],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 422


def test_submit_order_empty_items_list_returns_422(client):
    payload = {"customer": {"name": "Rajan", "phone_number": "9999999999"}, "items": []}

    response = client.post("/orders", json=payload)

    assert response.status_code == 422


def test_submit_order_nonexistent_menu_item_returns_404(client):
    payload = {
        "customer": {"name": "Rajan", "phone_number": "9999999999"},
        "items": [{"menu_item_id": 99999, "base_selected": "Thin Crust", "quantity": 1}],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 404


def test_submit_order_invalid_base_returns_409(client, menu_item):
    payload = {
        "customer": {"name": "Rajan", "phone_number": "9999999999"},
        "items": [{"menu_item_id": menu_item.id, "base_selected": "Nonexistent Crust", "quantity": 1}],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 409


def test_submit_order_invalid_topping_returns_409(client, menu_item):
    payload = {
        "customer": {"name": "Rajan", "phone_number": "9999999999"},
        "items": [
            {
                "menu_item_id": menu_item.id,
                "base_selected": "Thin Crust",
                "toppings_selected": ["Bacon"],
                "quantity": 1,
            }
        ],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 409


def test_submit_order_quantity_zero_returns_422(client, menu_item):
    payload = {
        "customer": {"name": "Rajan", "phone_number": "9999999999"},
        "items": [{"menu_item_id": menu_item.id, "base_selected": "Thin Crust", "quantity": 0}],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 422
