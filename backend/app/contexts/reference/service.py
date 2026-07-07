from app.contexts.reference.entities.base import Base
from app.contexts.reference.entities.menu_item import MenuItem
from app.contexts.reference.entities.topping import Topping
from app.contexts.reference.repositories.base_repository import BaseRepository
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.repositories.topping_repository import ToppingRepository
from app.contexts.reference.schemas.menu_schemas import (
    BaseResponse,
    MenuItemResponse,
    MenuResponse,
    ToppingResponse,
)


class MenuLoader:
    def __init__(
        self,
        repository: MenuRepository,
        base_repository: BaseRepository,
        topping_repository: ToppingRepository,
    ):
        self._repository = repository
        self._base_repository = base_repository
        self._topping_repository = topping_repository

    def load_menu(self) -> MenuResponse:
        items = self._repository.get_available_items()
        bases = self._base_repository.get_all()
        toppings = self._topping_repository.get_all()

        return MenuResponse(
            items=[MenuItemResponse.model_validate(item) for item in items],
            bases=[BaseResponse.model_validate(base) for base in bases],
            toppings=[ToppingResponse.model_validate(topping) for topping in toppings],
        )

    def seed_pizzas_from_file(self, filepath: str) -> None:
        if self._repository.count() > 0:
            return

        items = [
            MenuItem(code=code, name=name, category="Pizza", price=price, is_available=True)
            for code, name, price in self._parse_code_name_price(filepath)
        ]
        self._repository.save_items(items)

    def seed_bases_from_file(self, filepath: str) -> None:
        if self._base_repository.count() > 0:
            return

        items = [
            Base(code=code, name=name, price=price)
            for code, name, price in self._parse_code_name_price(filepath)
        ]
        self._base_repository.save_items(items)

    def seed_toppings_from_file(self, filepath: str) -> None:
        if self._topping_repository.count() > 0:
            return

        items = [
            Topping(code=code, name=name, price=price)
            for code, name, price in self._parse_code_name_price(filepath)
        ]
        self._topping_repository.save_items(items)

    @staticmethod
    def _parse_code_name_price(filepath: str) -> list[tuple[str, str, float]]:
        rows = []
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                code, name, price = line.split(";")
                rows.append((code, name, float(price)))
        return rows
