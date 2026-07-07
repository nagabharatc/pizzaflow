from typing import Optional

from sqlalchemy.orm import Session

from app.contexts.reference.entities.base import Base


class BaseRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_all(self) -> list[Base]:
        return self._db.query(Base).all()

    def get_by_name(self, name: str) -> Optional[Base]:
        return self._db.query(Base).filter(Base.name == name).first()

    def count(self) -> int:
        return self._db.query(Base).count()

    def save_items(self, items: list[Base]) -> None:
        self._db.add_all(items)
        self._db.commit()
