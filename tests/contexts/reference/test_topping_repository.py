import pytest

from app.contexts.reference.entities.topping import Topping
from app.contexts.reference.repositories.topping_repository import ToppingRepository


@pytest.fixture
def repository(db_session) -> ToppingRepository:
    return ToppingRepository(db_session)


@pytest.fixture
def seeded_toppings(db_session) -> list[Topping]:
    items = [
        Topping(code="T1", name="Mozzarella", price=69.0),
        Topping(code="T2", name="Jalapenos", price=39.0),
    ]
    db_session.add_all(items)
    db_session.commit()
    return items


def test_get_all_returns_all_toppings(repository, seeded_toppings):
    result = repository.get_all()

    assert len(result) == 2


def test_get_all_returns_empty_when_no_toppings(repository):
    result = repository.get_all()

    assert result == []


def test_get_by_name_returns_correct_topping(repository, seeded_toppings):
    result = repository.get_by_name("Mozzarella")

    assert result is not None
    assert result.price == 69.0


def test_get_by_name_returns_none_for_unknown_name(repository, seeded_toppings):
    result = repository.get_by_name("Bacon")

    assert result is None


def test_count_returns_number_of_toppings(repository, seeded_toppings):
    result = repository.count()

    assert result == 2


def test_count_returns_zero_when_empty(repository):
    result = repository.count()

    assert result == 0


def test_save_items_persists_to_database(repository, db_session):
    repository.save_items([Topping(code="T3", name="Bacon", price=79.0)])

    saved = db_session.query(Topping).filter_by(name="Bacon").first()
    assert saved is not None
    assert saved.price == 79.0
