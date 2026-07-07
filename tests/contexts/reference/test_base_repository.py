import pytest

from app.contexts.reference.entities.base import Base
from app.contexts.reference.repositories.base_repository import BaseRepository


@pytest.fixture
def repository(db_session) -> BaseRepository:
    return BaseRepository(db_session)


@pytest.fixture
def seeded_bases(db_session) -> list[Base]:
    items = [
        Base(code="B1", name="Thin Crust", price=149.0),
        Base(code="B2", name="Thick Crust", price=179.0),
    ]
    db_session.add_all(items)
    db_session.commit()
    return items


def test_get_all_returns_all_bases(repository, seeded_bases):
    result = repository.get_all()

    assert len(result) == 2


def test_get_all_returns_empty_when_no_bases(repository):
    result = repository.get_all()

    assert result == []


def test_get_by_name_returns_correct_base(repository, seeded_bases):
    result = repository.get_by_name("Thin Crust")

    assert result is not None
    assert result.price == 149.0


def test_get_by_name_returns_none_for_unknown_name(repository, seeded_bases):
    result = repository.get_by_name("Stuffed Crust")

    assert result is None


def test_count_returns_number_of_bases(repository, seeded_bases):
    result = repository.count()

    assert result == 2


def test_count_returns_zero_when_empty(repository):
    result = repository.count()

    assert result == 0


def test_save_items_persists_to_database(repository, db_session):
    repository.save_items([Base(code="B3", name="Stuffed Crust", price=229.0)])

    saved = db_session.query(Base).filter_by(name="Stuffed Crust").first()
    assert saved is not None
    assert saved.price == 229.0
