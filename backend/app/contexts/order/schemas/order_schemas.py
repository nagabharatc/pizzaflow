from datetime import datetime

from pydantic import BaseModel, Field


class CustomerRequest(BaseModel):
    name: str = Field(min_length=1, max_length=15, pattern=r"^[A-Za-z ]+$")
    phone_number: str = Field(pattern=r"^[6-9]\d{9}$")


class OrderItemRequest(BaseModel):
    menu_item_id: int
    base_selected: str = Field(min_length=1)
    toppings_selected: list[str] = []
    quantity: int = Field(ge=1, le=50)


class SubmitOrderRequest(BaseModel):
    customer: CustomerRequest
    items: list[OrderItemRequest] = Field(min_length=1)


class CustomerSummary(BaseModel):
    name: str
    phone_number: str

    model_config = {"from_attributes": True}


class OrderItemResponse(BaseModel):
    menu_item_id: int
    name: str
    base_selected: str
    toppings_selected: list[str]
    quantity: int
    unit_price: float


class PendingOrderResponse(BaseModel):
    order_id: int
    status: str
    customer: CustomerSummary
    items: list[OrderItemResponse]
    created_at: datetime
