from typing import Optional

from sqlalchemy.orm import Session

from app.contexts.reference.entities.topping import Topping


class ToppingRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_all(self) -> list[Topping]:
        return self._db.query(Topping).all()

    def get_by_name(self, name: str) -> Optional[Topping]:
        return self._db.query(Topping).filter(Topping.name == name).first()

    def count(self) -> int:
        return self._db.query(Topping).count()

    def save_items(self, items: list[Topping]) -> None:
        self._db.add_all(items)
        self._db.commit()
