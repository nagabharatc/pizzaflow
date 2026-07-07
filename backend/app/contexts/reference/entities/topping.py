from sqlalchemy import Column, Float, Integer, String

from app.shared.database import Base


class Topping(Base):
    __tablename__ = "toppings"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
