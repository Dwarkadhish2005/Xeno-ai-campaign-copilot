import pandas as pd

# -----------------------------
# Load Data
# -----------------------------

customers = pd.read_csv("output/customers.csv")

orders = pd.read_csv("output/orders.csv")

orders["order_date"] = pd.to_datetime(
    orders["order_date"]
)

# -----------------------------
# Customer Metrics
# -----------------------------

today = pd.Timestamp.today()

customer_profiles = (
    orders.groupby("customer_id")
    .agg(
        total_orders=("order_id", "count"),
        total_spend=("amount", "sum"),
        avg_order_value=("amount", "mean"),
        last_purchase_date=("order_date", "max")
    )
    .reset_index()
)

customer_profiles[
    "days_since_last_purchase"
] = (
    today -
    customer_profiles["last_purchase_date"]
).dt.days

# -----------------------------
# Segment Definitions
# -----------------------------

vip_customers = customer_profiles[
    customer_profiles["total_spend"] > 8000
]

dormant_customers = customer_profiles[
    customer_profiles["days_since_last_purchase"] > 60
]

frequent_buyers = customer_profiles[
    customer_profiles["total_orders"] >= 15
]

new_customers = customers[
    pd.to_datetime(customers["signup_date"])
    >= (today - pd.Timedelta(days=30))
]

at_risk_customers = customer_profiles[
    (
        customer_profiles[
            "days_since_last_purchase"
        ].between(20, 60)
    )
    &
    (
        customer_profiles["total_orders"] >= 8
    )
]

# -----------------------------
# Dataset Statistics
# -----------------------------

print("\n========== DATASET SUMMARY ==========\n")

print(
    f"Customers: {len(customers)}"
)

print(
    f"Orders: {len(orders)}"
)

print(
    f"Average Order Value: ₹{orders['amount'].mean():.2f}"
)

print(
    f"Total Revenue: ₹{orders['amount'].sum():,.2f}"
)

print("\n========== SEGMENTS ==========\n")

print(
    f"VIP Customers: {len(vip_customers)}"
)

print(
    f"Dormant Customers: {len(dormant_customers)}"
)

print(
    f"Frequent Buyers: {len(frequent_buyers)}"
)

print(
    f"New Customers: {len(new_customers)}"
)

print(
    f"At Risk Customers: {len(at_risk_customers)}"
)

# -----------------------------
# Top 10 Customers
# -----------------------------

print("\n========== TOP SPENDERS ==========\n")

print(
    customer_profiles
    .sort_values(
        "total_spend",
        ascending=False
    )
    .head(10)
    [
        [
            "customer_id",
            "total_spend",
            "total_orders"
        ]
    ]
)

# -----------------------------
# Save Profiles
# -----------------------------

customer_profiles.to_csv(
    "output/customer_profiles.csv",
    index=False
)

print(
    "\ncustomer_profiles.csv created"
)