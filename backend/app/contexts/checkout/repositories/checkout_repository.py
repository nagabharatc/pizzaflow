from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem


class CheckoutRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_pending_order(self, order_id: int) -> Optional[Order]:
        return (
            self._db.query(Order)
            .filter(Order.id == order_id, Order.status == "pending")
            .first()
        )

    def get_order_items(self, order_id: int) -> list[OrderItem]:
        return self._db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    def complete_transaction(
        self,
        order: Order,
        subtotal: float,
        discount_rate: float,
        discount_amount: float,
        gst_rate: float,
        gst_amount: float,
        total_amount: float,
        payment_method: str,
    ) -> tuple[Order, Bill, Payment]:
        order.status = "paid"
        order.updated_at = datetime.utcnow()

        bill = Bill(
            order_id=order.id,
            subtotal=subtotal,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            total_amount=total_amount,
        )
        self._db.add(bill)
        self._db.flush()

        payment = Payment(
            order_id=order.id,
            bill_id=bill.id,
            payment_method=payment_method,
            amount_paid=total_amount,
        )
        self._db.add(payment)
        self._db.commit()

        self._db.refresh(order)
        self._db.refresh(bill)
        self._db.refresh(payment)

        return order, bill, payment
