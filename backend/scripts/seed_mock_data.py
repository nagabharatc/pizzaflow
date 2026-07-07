"""
Seed 60 days of realistic mock order data for PizzaFlow AI testing.
Run from: /Users/rigdas/RESTURANT_MANAGEMENT/backend
  python ../scripts/seed_mock_data.py
"""
import sys, os, random, json
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")

from sqlalchemy import text
from app.shared.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

GST_RATE = 18.0

MENU = [
    {"id": 1, "name": "Margherita",     "price": 299.0,  "category": "Classic",  "bases": ["Thin Crust", "Thick Crust"], "toppings": ["Extra Cheese"]},
    {"id": 2, "name": "Pepperoni",      "price": 399.0,  "category": "Non-Veg",  "bases": ["Thin Crust", "Stuffed Crust"], "toppings": ["Extra Cheese", "Jalapeños"]},
    {"id": 3, "name": "Farmhouse",      "price": 349.0,  "category": "Veg",      "bases": ["Thin Crust", "Thick Crust"], "toppings": ["Extra Veggies", "Extra Cheese"]},
    {"id": 4, "name": "BBQ Chicken",    "price": 449.0,  "category": "Non-Veg",  "bases": ["Thin Crust", "Stuffed Crust"], "toppings": ["Extra Cheese", "Jalapeños"]},
    {"id": 5, "name": "Veggie Supreme", "price": 329.0,  "category": "Veg",      "bases": ["Thin Crust", "Thick Crust"], "toppings": ["Extra Veggies"]},
]

CUSTOMERS = [
    ("Priya Sharma",    "9876543210"),
    ("Rohan Gupta",     "9845012345"),
    ("Anita Desai",     "9723456789"),
    ("Vikram Nair",     "9612345678"),
    ("Sunita Patel",    "9501234567"),
    ("Amit Kumar",      "9390123456"),
    ("Kavita Joshi",    "9279012345"),
    ("Sanjay Mehta",    "9168901234"),
    ("Deepa Iyer",      "9057890123"),
    ("Rahul Verma",     "8946789012"),
    ("Meera Rao",       "8835678901"),
    ("Arun Bose",       "8724567890"),
    ("Pooja Singh",     "8613456789"),
    ("Kiran Pillai",    "8502345678"),
    ("Suresh Reddy",    "8391234567"),
]

PAYMENT_METHODS = ["card", "cash", "upi"]
# Weighted: card 45%, cash 30%, upi 25%
PAYMENT_WEIGHTS = [0.45, 0.30, 0.25]

def days_ago(n: int, hour: int = 12, minute: int = 0) -> datetime:
    d = datetime.now(timezone.utc) - timedelta(days=n)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0)

def make_order_items(menu_selections):
    """menu_selections: list of (menu_item_id, quantity)"""
    items = []
    for item_id, qty in menu_selections:
        m = next(x for x in MENU if x["id"] == item_id)
        base = random.choice(m["bases"])
        toppings = random.sample(m["toppings"], k=random.randint(0, min(1, len(m["toppings"]))))
        items.append({
            "menu_item_id": item_id,
            "base_selected": base,
            "toppings_selected": json.dumps(toppings),
            "quantity": qty,
            "unit_price": m["price"],
        })
    return items

def compute_bill(items):
    subtotal = sum(i["unit_price"] * i["quantity"] for i in items)
    gst_amount = round(subtotal * GST_RATE / 100, 2)
    total = round(subtotal + gst_amount, 2)
    return subtotal, gst_amount, total


# Orders to generate: (days_ago, customer_idx_in_new_list, [(menu_id, qty)], payment_method)
# Strategy: 65 orders spread over 60 days with visible growth
# - days 60-31: ~18 orders (older month)
# - days 30-8:  ~22 orders (current month, earlier)
# - days 7-1:   ~25 orders (current week — bigger, shows growth)

ORDER_PLAN = [
    # --- 60-31 days ago (older period, slower) ---
    (60, 0,  [(1, 1), (3, 1)],        "card"),
    (58, 1,  [(2, 2)],                "cash"),
    (57, 2,  [(4, 1)],                "upi"),
    (55, 3,  [(1, 1)],                "card"),
    (54, 4,  [(5, 2)],                "cash"),
    (52, 5,  [(2, 1), (4, 1)],        "card"),
    (51, 6,  [(3, 1)],                "upi"),
    (49, 0,  [(1, 2)],                "card"),   # returning customer
    (48, 7,  [(4, 1)],                "cash"),
    (46, 8,  [(5, 1), (1, 1)],        "upi"),
    (45, 9,  [(2, 1)],                "card"),
    (43, 1,  [(3, 2)],                "cash"),   # returning
    (42, 10, [(4, 1)],                "card"),
    (40, 11, [(1, 1), (2, 1)],        "upi"),
    (38, 2,  [(5, 1)],                "cash"),   # returning
    (37, 12, [(4, 2)],                "card"),
    (35, 3,  [(2, 1)],                "upi"),    # returning
    (33, 13, [(1, 1), (3, 1)],        "card"),

    # --- 30-8 days ago (current month, picking up) ---
    (30, 14, [(4, 1), (5, 1)],        "card"),
    (29, 0,  [(2, 1)],                "upi"),    # returning
    (28, 4,  [(1, 2), (3, 1)],        "card"),   # returning
    (27, 5,  [(4, 1)],                "cash"),   # returning
    (26, 6,  [(5, 2)],                "card"),   # returning
    (25, 7,  [(2, 1), (1, 1)],        "upi"),    # returning
    (24, 8,  [(4, 1)],                "card"),   # returning
    (23, 9,  [(3, 1), (5, 1)],        "cash"),   # returning
    (22, 10, [(2, 2)],                "card"),   # returning
    (21, 11, [(1, 1)],                "upi"),    # returning
    (20, 1,  [(4, 1), (2, 1)],        "card"),   # returning
    (19, 12, [(5, 1)],                "cash"),   # returning
    (18, 2,  [(1, 2)],                "card"),   # returning
    (17, 13, [(3, 1), (4, 1)],        "upi"),    # returning
    (16, 3,  [(2, 1)],                "card"),   # returning
    (15, 14, [(5, 2), (1, 1)],        "cash"),   # returning
    (14, 0,  [(4, 1)],                "upi"),    # returning
    (13, 4,  [(1, 1), (3, 1)],        "card"),   # returning
    (12, 6,  [(2, 2)],                "cash"),   # returning
    (11, 7,  [(4, 1), (5, 1)],        "card"),   # returning
    (10, 8,  [(3, 1)],                "upi"),    # returning
    (9,  5,  [(1, 1), (2, 1)],        "card"),   # returning
    (8,  9,  [(4, 2)],                "cash"),   # returning

    # --- Last 7 days (strong week, shows growth) ---
    (7,  10, [(2, 1), (4, 1)],        "card"),
    (7,  11, [(1, 2)],                "upi"),
    (6,  12, [(5, 1), (3, 1)],        "card"),
    (6,  0,  [(4, 1)],                "cash"),   # returning
    (6,  1,  [(2, 2)],                "card"),   # returning
    (5,  13, [(1, 1), (5, 1)],        "upi"),
    (5,  2,  [(4, 1), (3, 1)],        "card"),   # returning
    (5,  14, [(2, 1)],                "cash"),   # returning
    (4,  3,  [(5, 2), (1, 1)],        "card"),   # returning
    (4,  4,  [(4, 1)],                "upi"),    # returning
    (4,  6,  [(2, 1), (5, 1)],        "card"),   # returning
    (3,  7,  [(1, 2)],                "cash"),   # returning
    (3,  8,  [(4, 1), (2, 1)],        "card"),   # returning
    (3,  9,  [(3, 1)],                "upi"),    # returning
    (2,  10, [(5, 1), (4, 1)],        "card"),   # returning
    (2,  11, [(1, 1), (2, 1)],        "cash"),   # returning
    (2,  5,  [(4, 2)],                "card"),   # returning
    (1,  12, [(3, 1), (5, 1)],        "upi"),    # returning
    (1,  13, [(2, 1)],                "card"),   # returning
    (1,  14, [(1, 1), (4, 1)],        "card"),   # returning
    (1,  0,  [(5, 1)],                "cash"),   # returning
]

def seed():
    with SessionLocal() as db:
        # Insert new customers
        customer_ids = []
        for name, phone in CUSTOMERS:
            existing = db.execute(
                text("SELECT id FROM customers WHERE phone_number = :p"),
                {"p": phone}
            ).fetchone()
            if existing:
                customer_ids.append(existing[0])
            else:
                result = db.execute(
                    text("INSERT INTO customers (name, phone_number, created_at) VALUES (:n, :p, :c) RETURNING id"),
                    {"n": name, "p": phone, "c": datetime.now(timezone.utc)}
                )
                customer_ids.append(result.fetchone()[0])
        db.commit()
        print(f"Customers ready: {len(customer_ids)} new customers (IDs {customer_ids[0]}–{customer_ids[-1]})")

        inserted = 0
        for day_offset, cust_idx, selections, pay_method in ORDER_PLAN:
            customer_id = customer_ids[cust_idx]
            order_time = days_ago(day_offset, hour=random.randint(11, 21), minute=random.randint(0, 59))

            # Insert order
            order_result = db.execute(
                text("""INSERT INTO orders (customer_id, status, created_at, updated_at)
                        VALUES (:c, 'paid', :t, :t) RETURNING id"""),
                {"c": customer_id, "t": order_time}
            )
            order_id = order_result.fetchone()[0]

            # Insert order items
            items = make_order_items(selections)
            for item in items:
                db.execute(
                    text("""INSERT INTO order_items
                            (order_id, menu_item_id, base_selected, toppings_selected, quantity, unit_price)
                            VALUES (:o, :m, :b, :t, :q, :p)"""),
                    {
                        "o": order_id,
                        "m": item["menu_item_id"],
                        "b": item["base_selected"],
                        "t": item["toppings_selected"],
                        "q": item["quantity"],
                        "p": item["unit_price"],
                    }
                )

            # Compute bill
            subtotal, gst_amount, total = compute_bill(items)

            # Insert bill
            bill_result = db.execute(
                text("""INSERT INTO bills (order_id, subtotal, gst_rate, gst_amount, total_amount, created_at)
                        VALUES (:o, :s, :r, :g, :t, :c) RETURNING id"""),
                {
                    "o": order_id, "s": subtotal, "r": GST_RATE,
                    "g": gst_amount, "t": total, "c": order_time
                }
            )
            bill_id = bill_result.fetchone()[0]

            # Insert payment
            db.execute(
                text("""INSERT INTO payments (order_id, bill_id, payment_method, amount_paid, created_at)
                        VALUES (:o, :b, :m, :a, :c)"""),
                {
                    "o": order_id, "b": bill_id,
                    "m": pay_method, "a": total, "c": order_time
                }
            )
            inserted += 1

        db.commit()
        print(f"Inserted {inserted} orders with bills and payments.")

        # Summary
        total_orders = db.execute(text("SELECT COUNT(*) FROM orders WHERE status='paid'")).scalar()
        total_revenue = db.execute(text("SELECT SUM(total_amount) FROM bills")).scalar()
        print(f"\nDatabase totals: {total_orders} paid orders | ₹{total_revenue:,.2f} total revenue")


if __name__ == "__main__":
    seed()
