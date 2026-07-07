import pytest

from app.contexts.checkout.entities.discount_settings import DiscountSettings
from app.contexts.checkout.repositories.discount_settings_repository import (
    DEFAULT_QUANTITY_THRESHOLD,
    DiscountSettingsRepository,
)


@pytest.fixture
def repository(db_session) -> DiscountSettingsRepository:
    return DiscountSettingsRepository(db_session)


def test_get_quantity_threshold_returns_seeded_value(repository, db_session):
    db_session.add(DiscountSettings(quantity_threshold=8))
    db_session.commit()

    result = repository.get_quantity_threshold()

    assert result == 8


def test_get_quantity_threshold_falls_back_to_default_when_empty(repository):
    result = repository.get_quantity_threshold()

    assert result == DEFAULT_QUANTITY_THRESHOLD


def test_count_returns_number_of_rows(repository, db_session):
    assert repository.count() == 0

    db_session.add(DiscountSettings(quantity_threshold=5))
    db_session.commit()

    assert repository.count() == 1


def test_seed_default_if_empty_creates_row_when_none_exists(repository, db_session):
    repository.seed_default_if_empty()

    row = db_session.query(DiscountSettings).first()
    assert row is not None
    assert row.quantity_threshold == DEFAULT_QUANTITY_THRESHOLD


def test_seed_default_if_empty_does_not_duplicate_existing_row(repository, db_session):
    db_session.add(DiscountSettings(quantity_threshold=7))
    db_session.commit()

    repository.seed_default_if_empty()

    assert repository.count() == 1
    assert repository.get_quantity_threshold() == 7
