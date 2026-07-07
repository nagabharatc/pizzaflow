from pydantic import BaseModel


class MenuItemResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    price: float

    model_config = {"from_attributes": True}


class BaseResponse(BaseModel):
    id: int
    code: str
    name: str
    price: float

    model_config = {"from_attributes": True}


class ToppingResponse(BaseModel):
    id: int
    code: str
    name: str
    price: float

    model_config = {"from_attributes": True}


class MenuResponse(BaseModel):
    items: list[MenuItemResponse]
    bases: list[BaseResponse]
    toppings: list[ToppingResponse]
