from sqlalchemy import Column, Integer

from app.shared.database import Base


class DiscountSettings(Base):
    __tablename__ = "discount_settings"

    id = Column(Integer, primary_key=True, index=True)
    quantity_threshold = Column(Integer, nullable=False, default=5)
