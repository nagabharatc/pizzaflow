import pytest

from app.contexts.checkout.entities.bill import Bill
from app.contexts.checkout.entities.payment import Payment
from app.contexts.checkout.repositories.checkout_repository import CheckoutRepository
from app.contexts.order.entities.customer import Customer
from app.contexts.order.entities.order import Order
from app.contexts.order.entities.order_item import OrderItem
from app.contexts.reference.entities.menu_item import MenuItem


@pytest.fixture
def repository(db_session) -> CheckoutRepository:
    return CheckoutRepository(db_session)


@pytest.fixture
def saved_pending_order(db_session) -> Order:
    customer = Customer(name="Rajan", phone_number="9999999999")
    db_session.add(customer)
    db_session.flush()

    order = Order(customer_id=customer.id, status="pending")
    db_session.add(order)
    db_session.flush()

    menu_item = MenuItem(
        code="P1", name="Margherita", category="Pizza",
        price=299.0, is_available=True,
    )
    db_session.add(menu_item)
    db_session.flush()

    item = OrderItem(
        order_id=order.id, menu_item_id=menu_item.id,
        base_selected="Thin Crust", toppings_selected=[],
        quantity=2, unit_price=299.0,
    )
    db_session.add(item)
    db_session.commit()

    return order


def test_get_pending_order_returns_pending_order(repository, saved_pending_order):
    result = repository.get_pending_order(saved_pending_order.id)

    assert result is not None
    assert result.id == saved_pending_order.id
    assert result.status == "pending"


def test_get_pending_order_returns_none_for_nonexistent_id(repository):
    result = repository.get_pending_order(99999)

    assert result is None


def test_get_pending_order_returns_none_for_paid_order(repository, saved_pending_order, db_session):
    saved_pending_order.status = "paid"
    db_session.commit()

    result = repository.get_pending_order(saved_pending_order.id)

    assert result is None


def test_get_order_items_returns_all_items(repository, saved_pending_order):
    result = repository.get_order_items(saved_pending_order.id)

    assert len(result) == 1
    assert result[0].order_id == saved_pending_order.id
    assert result[0].unit_price == 299.0


def test_complete_transaction_sets_order_status_to_paid(repository, saved_pending_order):
    items = repository.get_order_items(saved_pending_order.id)
    subtotal = sum(i.unit_price * i.quantity for i in items)

    order, bill, payment = repository.complete_transaction(
        order=saved_pending_order,
        subtotal=subtotal,
        discount_rate=0.0,
        discount_amount=0.0,
        gst_rate=18.0,
        gst_amount=round(subtotal * 0.18, 2),
        total_amount=round(subtotal * 1.18, 2),
        payment_method="card",
    )

    assert order.status == "paid"


def test_complete_transaction_persists_bill_with_gst_rate(repository, saved_pending_order, db_session):
    items = repository.get_order_items(saved_pending_order.id)
    subtotal = sum(i.unit_price * i.quantity for i in items)
    gst_amount = round(subtotal * 0.18, 2)
    total = round(subtotal + gst_amount, 2)

    order, bill, payment = repository.complete_transaction(
        order=saved_pending_order,
        subtotal=subtotal,
        discount_rate=0.0,
        discount_amount=0.0,
        gst_rate=18.0,
        gst_amount=gst_amount,
        total_amount=total,
        payment_method="cash",
    )

    assert bill.id is not None
    assert bill.gst_rate == 18.0
    assert bill.subtotal == subtotal
    assert bill.total_amount == total

    in_db = db_session.query(Bill).filter_by(order_id=saved_pending_order.id).first()
    assert in_db is not None


def test_complete_transaction_persists_payment(repository, saved_pending_order, db_session):
    items = repository.get_order_items(saved_pending_order.id)
    subtotal = sum(i.unit_price * i.quantity for i in items)
    total = round(subtotal * 1.18, 2)

    order, bill, payment = repository.complete_transaction(
        order=saved_pending_order,
        subtotal=subtotal,
        discount_rate=0.0,
        discount_amount=0.0,
        gst_rate=18.0,
        gst_amount=round(subtotal * 0.18, 2),
        total_amount=total,
        payment_method="upi",
    )

    assert payment.id is not None
    assert payment.payment_method == "upi"
    assert payment.amount_paid == total
    assert payment.bill_id == bill.id

    in_db = db_session.query(Payment).filter_by(order_id=saved_pending_order.id).first()
    assert in_db is not None


def test_complete_transaction_links_payment_to_bill(repository, saved_pending_order):
    items = repository.get_order_items(saved_pending_order.id)
    subtotal = sum(i.unit_price * i.quantity for i in items)

    order, bill, payment = repository.complete_transaction(
        order=saved_pending_order,
        subtotal=subtotal,
        discount_rate=0.0,
        discount_amount=0.0,
        gst_rate=18.0,
        gst_amount=round(subtotal * 0.18, 2),
        total_amount=round(subtotal * 1.18, 2),
        payment_method="card",
    )

    assert payment.bill_id == bill.id
    assert payment.order_id == bill.order_id


def test_complete_transaction_persists_nonzero_discount(repository, saved_pending_order, db_session):
    items = repository.get_order_items(saved_pending_order.id)
    subtotal = sum(i.unit_price * i.quantity for i in items)
    discount_amount = round(subtotal * 0.10, 2)
    taxable = round(subtotal - discount_amount, 2)
    gst_amount = round(taxable * 0.18, 2)
    total = round(taxable + gst_amount, 2)

    order, bill, payment = repository.complete_transaction(
        order=saved_pending_order,
        subtotal=subtotal,
        discount_rate=10.0,
        discount_amount=discount_amount,
        gst_rate=18.0,
        gst_amount=gst_amount,
        total_amount=total,
        payment_method="card",
    )

    assert bill.discount_rate == 10.0
    assert bill.discount_amount == discount_amount

    in_db = db_session.query(Bill).filter_by(order_id=saved_pending_order.id).first()
    assert in_db.discount_rate == 10.0
    assert in_db.discount_amount == discount_amount
