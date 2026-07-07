from sqlalchemy.orm import Session

from app.contexts.checkout.entities.discount_settings import DiscountSettings

DEFAULT_QUANTITY_THRESHOLD = 5


class DiscountSettingsRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_quantity_threshold(self) -> int:
        settings = self._db.query(DiscountSettings).first()
        return settings.quantity_threshold if settings is not None else DEFAULT_QUANTITY_THRESHOLD

    def count(self) -> int:
        return self._db.query(DiscountSettings).count()

    def seed_default_if_empty(self) -> None:
        if self.count() > 0:
            return

        self._db.add(DiscountSettings(quantity_threshold=DEFAULT_QUANTITY_THRESHOLD))
        self._db.commit()
