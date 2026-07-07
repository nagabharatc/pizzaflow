import pytest

from app.contexts.reference.entities.base import Base
from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.entities.topping import Topping


@pytest.fixture
def available_menu_items(db_session) -> list[MenuItem]:
    items = [
        MenuItem(code="P1", name="Margherita", category="Pizza", price=299.0, is_available=True),
        MenuItem(code="P2", name="Pepperoni", category="Pizza", price=399.0, is_available=True),
        MenuItem(code="P3", name="Discontinued", category="Pizza", price=199.0, is_available=False),
    ]
    db_session.add_all(items)
    db_session.add_all([
        Base(code="B1", name="Thin Crust", price=149.0),
        Base(code="B2", name="Thick Crust", price=179.0),
    ])
    db_session.add_all([
        Topping(code="T1", name="Mozzarella", price=69.0),
    ])
    db_session.commit()
    return items


def test_retrieve_menu_returns_200(client):
    response = client.get("/menu")

    assert response.status_code == 200


def test_retrieve_menu_response_structure(client, available_menu_items):
    response = client.get("/menu")
    body = response.json()

    assert "items" in body
    assert isinstance(body["items"], list)


def test_retrieve_menu_excludes_unavailable_items(client, available_menu_items):
    response = client.get("/menu")
    items = response.json()["items"]

    assert len(items) == 2
    names = {item["name"] for item in items}
    assert "Discontinued" not in names


def test_retrieve_menu_item_has_required_fields(client, available_menu_items):
    response = client.get("/menu")
    item = response.json()["items"][0]

    assert "id" in item
    assert "code" in item
    assert "name" in item
    assert "category" in item
    assert "price" in item


def test_retrieve_menu_returns_empty_list_when_no_items(client):
    response = client.get("/menu")
    body = response.json()

    assert body["items"] == []


def test_retrieve_menu_includes_bases_and_toppings(client, available_menu_items):
    response = client.get("/menu")
    body = response.json()

    assert isinstance(body["bases"], list)
    assert isinstance(body["toppings"], list)
    assert len(body["bases"]) == 2
    assert len(body["toppings"]) == 1
    assert body["bases"][0]["name"] == "Thin Crust"
    assert body["bases"][0]["price"] == 149.0
