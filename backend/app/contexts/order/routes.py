from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.contexts.reference.repositories.base_repository import BaseRepository
from app.contexts.reference.repositories.menu_repository import MenuRepository
from app.contexts.reference.repositories.topping_repository import ToppingRepository
from app.contexts.order.repositories.order_repository import OrderRepository
from app.contexts.order.schemas.order_schemas import PendingOrderResponse, SubmitOrderRequest
from app.contexts.order.service import OrderService


router = APIRouter()


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(
        order_repository=OrderRepository(db),
        menu_repository=MenuRepository(db),
        base_repository=BaseRepository(db),
        topping_repository=ToppingRepository(db),
    )


@router.post("", response_model=PendingOrderResponse, status_code=201)
def submit_order(
    request: SubmitOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> PendingOrderResponse:
    return service.submit_order(request.customer, request.items)
