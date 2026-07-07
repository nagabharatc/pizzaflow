from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer

from app.shared.database import Base


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    subtotal = Column(Float, nullable=False)
    discount_rate = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    gst_rate = Column(Float, nullable=False)
    gst_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
