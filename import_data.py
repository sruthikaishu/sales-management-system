import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost", user="root", password="root",
    database="sales_management_system"
)
cur = conn.cursor()


def rows(df):
    return [
        tuple(None if pd.isna(v) else (v.item() if hasattr(v, "item") else v) for v in r)
        for r in df.itertuples(index=False)
    ]


branches = pd.read_csv("branches.csv")
users = pd.read_csv("users.csv")
users["branch_id"] = users["branch_id"].astype("Int64")
sales = pd.read_csv("customer_sales.csv")
payments = pd.read_csv("payment_splits.csv")

# clear old data
cur.execute("SET FOREIGN_KEY_CHECKS = 0")
for t in ["payment_splits", "customer_sales", "users", "branches"]:
    cur.execute(f"TRUNCATE TABLE {t}")
cur.execute("SET FOREIGN_KEY_CHECKS = 1")

# insert in this order (parents first)
cur.executemany(
    "INSERT INTO branches (branch_id, branch_name, branch_admin_name) VALUES (%s, %s, %s)",
    rows(branches),
)
cur.executemany(
    "INSERT INTO users (user_id, username, password, branch_id, role, email) "
    "VALUES (%s, %s, %s, %s, %s, %s)",
    rows(users),
)
cur.executemany(
    "INSERT INTO customer_sales (sale_id, branch_id, date, name, mobile_number, "
    "product_name, gross_sales, received_amount, status) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
    rows(sales),
)
# payments last, so the trigger updates received amount and status
cur.executemany(
    "INSERT INTO payment_splits (payment_id, sale_id, payment_date, amount_paid, payment_method) "
    "VALUES (%s, %s, %s, %s, %s)",
    rows(payments),
)
conn.commit()

for t in ["branches", "users", "customer_sales", "payment_splits"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(t, cur.fetchone()[0])
conn.close()