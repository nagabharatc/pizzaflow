from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CompleteCheckoutRequest(BaseModel):
    pending_order_id: int
    payment_method: Literal["cash", "card", "upi"]


class BillResponse(BaseModel):
    subtotal: float
    discount_rate: float
    discount_amount: float
    gst_rate: float
    gst_amount: float
    total_amount: float


class CheckoutItemResponse(BaseModel):
    name: str
    base_selected: str
    toppings_selected: list[str]
    quantity: int
    unit_price: float
    line_total: float


class CompleteCheckoutResponse(BaseModel):
    order_id: int
    status: str
    items: list[CheckoutItemResponse]
    bill: BillResponse
    payment_method: str
    paid_at: datetime
