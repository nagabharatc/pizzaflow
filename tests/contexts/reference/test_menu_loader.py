from unittest.mock import MagicMock

import pytest

from app.contexts.reference.entities.base import Base
from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.entities.topping import Topping
from app.contexts.reference.repositories.base_repository import BaseRepository
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.repositories.topping_repository import ToppingRepository
from app.contexts.reference.schemas.menu_schemas import MenuResponse
from app.contexts.reference.service import MenuLoader


@pytest.fixture
def mock_repository() -> MenuRepository:
    return MagicMock(spec=MenuRepository)


@pytest.fixture
def mock_base_repository() -> BaseRepository:
    return MagicMock(spec=BaseRepository)


@pytest.fixture
def mock_topping_repository() -> ToppingRepository:
    return MagicMock(spec=ToppingRepository)


@pytest.fixture
def service(mock_repository, mock_base_repository, mock_topping_repository) -> MenuLoader:
    return MenuLoader(mock_repository, mock_base_repository, mock_topping_repository)


def test_load_menu_returns_menu_response(service, mock_repository, mock_base_repository, mock_topping_repository):
    mock_repository.get_available_items.return_value = [
        MenuItem(id=1, code="P1", name="Margherita", category="Pizza", price=299.0, is_available=True),
    ]
    mock_base_repository.get_all.return_value = []
    mock_topping_repository.get_all.return_value = []

    result = service.load_menu()

    assert isinstance(result, MenuResponse)
    assert len(result.items) == 1
    assert result.items[0].name == "Margherita"
    assert result.items[0].price == 299.0


def test_load_menu_returns_empty_list_when_no_items(service, mock_repository, mock_base_repository, mock_topping_repository):
    mock_repository.get_available_items.return_value = []
    mock_base_repository.get_all.return_value = []
    mock_topping_repository.get_all.return_value = []

    result = service.load_menu()

    assert result.items == []
    mock_repository.get_available_items.assert_called_once()


def test_load_menu_includes_bases_and_toppings(service, mock_repository, mock_base_repository, mock_topping_repository):
    mock_repository.get_available_items.return_value = []
    mock_base_repository.get_all.return_value = [Base(id=1, code="B1", name="Thin Crust", price=149.0)]
    mock_topping_repository.get_all.return_value = [Topping(id=1, code="T1", name="Mozzarella", price=69.0)]

    result = service.load_menu()

    assert len(result.bases) == 1
    assert result.bases[0].name == "Thin Crust"
    assert len(result.toppings) == 1
    assert result.toppings[0].name == "Mozzarella"


def test_seed_pizzas_skips_when_database_already_populated(service, mock_repository, tmp_path):
    mock_repository.count.return_value = 3

    txt_file = tmp_path / "pizzas.txt"
    txt_file.write_text("P1;Margherita;299\n")

    service.seed_pizzas_from_file(str(txt_file))

    mock_repository.save_items.assert_not_called()


def test_seed_pizzas_loads_items_from_file_when_empty(service, mock_repository, tmp_path):
    mock_repository.count.return_value = 0

    txt_file = tmp_path / "pizzas.txt"
    txt_file.write_text("P1;Margherita;299\nP2;Pepperoni;399\nP3;Farmhouse;349\n")

    service.seed_pizzas_from_file(str(txt_file))

    mock_repository.save_items.assert_called_once()
    saved = mock_repository.save_items.call_args[0][0]
    assert len(saved) == 3
    assert saved[0].code == "P1"
    assert saved[0].name == "Margherita"
    assert saved[0].price == 299.0
    assert saved[0].category == "Pizza"


def test_seed_bases_loads_items_from_file_when_empty(service, mock_base_repository, tmp_path):
    mock_base_repository.count.return_value = 0

    txt_file = tmp_path / "bases.txt"
    txt_file.write_text("B1;Thin Crust;149\nB2;Thick Crust;179\nB3;Stuffed Crust;229\n")

    service.seed_bases_from_file(str(txt_file))

    mock_base_repository.save_items.assert_called_once()
    saved = mock_base_repository.save_items.call_args[0][0]
    assert len(saved) == 3
    assert saved[0].code == "B1"
    assert saved[0].name == "Thin Crust"
    assert saved[0].price == 149.0


def test_seed_toppings_loads_items_from_file_when_empty(service, mock_topping_repository, tmp_path):
    mock_topping_repository.count.return_value = 0

    txt_file = tmp_path / "toppings.txt"
    txt_file.write_text("T1;Mozzarella;69\nT2;Pepperoni;69\nT3;Jalapenos;39\n")

    service.seed_toppings_from_file(str(txt_file))

    mock_topping_repository.save_items.assert_called_once()
    saved = mock_topping_repository.save_items.call_args[0][0]
    assert len(saved) == 3
    assert saved[0].code == "T1"
    assert saved[0].name == "Mozzarella"
    assert saved[0].price == 69.0
