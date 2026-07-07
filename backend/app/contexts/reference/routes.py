from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.contexts.reference.repositories.base_repository import BaseRepository
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.repositories.topping_repository import ToppingRepository
from app.contexts.reference.schemas.menu_schemas import MenuResponse
from app.contexts.reference.service import MenuLoader


router = APIRouter()


def get_menu_loader(db: Session = Depends(get_db)) -> MenuLoader:
    return MenuLoader(MenuRepository(db), BaseRepository(db), ToppingRepository(db))


@router.get("", response_model=MenuResponse)
def retrieve_menu(loader: MenuLoader = Depends(get_menu_loader)) -> MenuResponse:
    return loader.load_menu()
