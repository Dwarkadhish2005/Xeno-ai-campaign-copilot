from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
import os

# -----------------------------
# Configuration
# -----------------------------

NUM_CUSTOMERS = 1000

OUTPUT_DIR = "output"

random.seed(42)

fake = Faker("en_IN")
Faker.seed(42)

# -----------------------------
# Create Output Directory
# -----------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Cities & Categories
# -----------------------------

cities = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Pune",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Ahmedabad"
]

categories = [
    "Latte",
    "Espresso",
    "Cappuccino",
    "Americano",
    "Mocha",
    "Cold Coffee"
]

# -----------------------------
# Generate Customers
# -----------------------------

customers = []

for customer_id in range(1, NUM_CUSTOMERS + 1):

    customers.append({
        "customer_id": customer_id,
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.msisdn()[:10],
        "city": random.choice(cities),
        "signup_date": fake.date_between(
            start_date="-2y",
            end_date="today"
        )
    })

customers_df = pd.DataFrame(customers)

customers_df.to_csv(
    f"{OUTPUT_DIR}/customers.csv",
    index=False
)

print(f"Customers Generated: {len(customers_df)}")

# -----------------------------
# Customer Segmentation
# -----------------------------

customer_ids = customers_df["customer_id"].tolist()

random.shuffle(customer_ids)

vip_customers = customer_ids[:100]

dormant_customers = customer_ids[100:250]

frequent_customers = customer_ids[250:450]

new_customers = customer_ids[450:550]

at_risk_customers = customer_ids[550:700]

regular_customers = customer_ids[700:]

# -----------------------------
# Generate Orders
# -----------------------------

orders = []

order_id = 1

today = datetime.now()

# -----------------------------
# VIP Customers
# -----------------------------

for customer_id in vip_customers:

    num_orders = random.randint(15, 25)

    for _ in range(num_orders):

        order_date = today - timedelta(
            days=random.randint(1, 180)
        )

        amount = random.randint(700, 1200)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.date(),
            "category": random.choice(categories)
        })

        order_id += 1

# -----------------------------
# Dormant Customers
# -----------------------------

for customer_id in dormant_customers:

    num_orders = random.randint(8, 15)

    for _ in range(num_orders):

        order_date = today - timedelta(
            days=random.randint(60, 365)
        )

        amount = random.randint(250, 700)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.date(),
            "category": random.choice(categories)
        })

        order_id += 1

# -----------------------------
# Frequent Buyers
# -----------------------------

for customer_id in frequent_customers:

    num_orders = random.randint(18, 30)

    for _ in range(num_orders):

        order_date = today - timedelta(
            days=random.randint(1, 180)
        )

        amount = random.randint(200, 600)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.date(),
            "category": random.choice(categories)
        })

        order_id += 1

# -----------------------------
# New Customers
# -----------------------------

for customer_id in new_customers:

    num_orders = random.randint(1, 3)

    for _ in range(num_orders):

        order_date = today - timedelta(
            days=random.randint(1, 30)
        )

        amount = random.randint(150, 500)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.date(),
            "category": random.choice(categories)
        })

        order_id += 1

# -----------------------------
# At Risk Customers
# -----------------------------

for customer_id in at_risk_customers:

    num_orders = random.randint(10, 18)

    for _ in range(num_orders):

        order_date = today - timedelta(
            days=random.randint(20, 120)
        )

        amount = random.randint(250, 700)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.date(),
            "category": random.choice(categories)
        })

        order_id += 1

# -----------------------------
# Regular Customers
# -----------------------------

for customer_id in regular_customers:

    num_orders = random.randint(3, 10)

    for _ in range(num_orders):

        order_date = today - timedelta(
            days=random.randint(1, 365)
        )

        amount = random.randint(150, 700)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "order_date": order_date.date(),
            "category": random.choice(categories)
        })

        order_id += 1

# -----------------------------
# Save Orders
# -----------------------------

orders_df = pd.DataFrame(orders)

orders_df.to_csv(
    f"{OUTPUT_DIR}/orders.csv",
    index=False
)

print(f"Orders Generated: {len(orders_df)}")

# -----------------------------
# Quick Summary
# -----------------------------

print("\nDataset Summary")
print("-" * 40)
print(f"Customers : {len(customers_df)}")
print(f"Orders    : {len(orders_df)}")
print(f"VIP       : {len(vip_customers)}")
print(f"Dormant   : {len(dormant_customers)}")
print(f"Frequent  : {len(frequent_customers)}")
print(f"New       : {len(new_customers)}")
print(f"At Risk   : {len(at_risk_customers)}")
print(f"Regular   : {len(regular_customers)}")