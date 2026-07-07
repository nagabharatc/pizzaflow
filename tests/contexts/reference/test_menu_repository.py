import pytest

from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.repositories.menu_repository import MenuRepository


@pytest.fixture
def repository(db_session) -> MenuRepository:
    return MenuRepository(db_session)


@pytest.fixture
def seeded_items(db_session) -> list[MenuItem]:
    items = [
        MenuItem(code="P1", name="Margherita", category="Pizza", price=299.0, is_available=True),
        MenuItem(code="P2", name="Pepperoni", category="Pizza", price=399.0, is_available=True),
        MenuItem(code="P3", name="Discontinued Pizza", category="Pizza", price=199.0, is_available=False),
    ]
    db_session.add_all(items)
    db_session.commit()
    return items


def test_get_available_items_excludes_unavailable(repository, seeded_items):
    result = repository.get_available_items()

    assert len(result) == 2
    assert all(item.is_available for item in result)
    names = {item.name for item in result}
    assert "Discontinued Pizza" not in names


def test_get_available_items_returns_empty_when_no_menu(repository):
    result = repository.get_available_items()

    assert result == []


def test_get_by_id_returns_correct_item(repository, seeded_items):
    target = seeded_items[0]

    result = repository.get_by_id(target.id)

    assert result is not None
    assert result.name == "Margherita"
    assert result.price == 299.0


def test_get_by_id_returns_none_for_nonexistent_id(repository):
    result = repository.get_by_id(99999)

    assert result is None


def test_count_includes_all_items_including_unavailable(repository, seeded_items):
    result = repository.count()

    assert result == 3


def test_count_returns_zero_when_empty(repository):
    result = repository.count()

    assert result == 0


def test_save_items_persists_to_database(repository, db_session):
    new_items = [
        MenuItem(code="P4", name="Farmhouse", category="Pizza", price=349.0, is_available=True),
    ]

    repository.save_items(new_items)

    saved = db_session.query(MenuItem).filter_by(name="Farmhouse").first()
    assert saved is not None
    assert saved.price == 349.0
    assert saved.code == "P4"
