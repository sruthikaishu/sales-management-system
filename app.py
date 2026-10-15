import streamlit as st
import mysql.connector
import pandas as pd

st.set_page_config(page_title="Sales Management System")


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="sales_management_system"
    )


def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user


if "user" not in st.session_state:
    st.session_state.user = None

# Login page
if st.session_state.user is None:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = check_login(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Wrong username or password")
    st.stop()

# Dashboard (only after login)
user = st.session_state.user
st.sidebar.write(f"Logged in as: {user['username']} ({user['role']})")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

st.title("Sales Management System")

conn = get_connection()
cursor = conn.cursor()
if user["role"] == "Super Admin":
    cursor.execute("SELECT * FROM customer_sales")
else:
    cursor.execute(
        "SELECT * FROM customer_sales WHERE branch_id = %s",
        (user["branch_id"],)
    )
rows = cursor.fetchall()
columns = [c[0] for c in cursor.description]
conn.close()

df = pd.DataFrame(rows, columns=columns)

# branch names for the filter
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT branch_id, branch_name FROM branches")
branch_rows = cursor.fetchall()
conn.close()
branch_names = {bid: name for bid, name in branch_rows}
df["branch"] = df["branch_id"].map(branch_names)

# ---------- Filters ----------
st.subheader("Filters")
f1, f2, f3, f4 = st.columns(4)

with f1:
    if user["role"] == "Super Admin":
        branch_choice = st.selectbox(
            "Branch", ["All"] + sorted(df["branch"].dropna().unique().tolist())
        )
    else:
        st.write(f"Branch: {branch_names.get(user['branch_id'])}")
        branch_choice = "All"
with f2:
    product_choice = st.selectbox(
        "Product", ["All"] + sorted(df["product_name"].dropna().unique().tolist())
    )
with f3:
    start_date = st.date_input("Start date", value=None)
with f4:
    end_date = st.date_input("End date", value=None)

fdf = df.copy()
if branch_choice != "All":
    fdf = fdf[fdf["branch"] == branch_choice]
if product_choice != "All":
    fdf = fdf[fdf["product_name"] == product_choice]
if start_date:
    fdf = fdf[pd.to_datetime(fdf["date"]) >= pd.to_datetime(start_date)]
if end_date:
    fdf = fdf[pd.to_datetime(fdf["date"]) <= pd.to_datetime(end_date)]

total_sales = float(fdf["gross_sales"].sum())
total_received = float(fdf["received_amount"].sum())
total_pending = float(fdf["pending_amount"].sum())

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"₹{total_sales:,.0f}")
col2.metric("Received", f"₹{total_received:,.0f}")
col3.metric("Pending", f"₹{total_pending:,.0f}")

st.subheader("All Sales")
st.dataframe(fdf)  
st.subheader("Reports")

if fdf.empty:
    st.info("No data for these filters.")
else:
    r1, r2 = st.columns(2)
    with r1:
        st.write("Sales by branch")
        st.bar_chart(fdf.groupby("branch")["gross_sales"].sum().astype(float))
    with r2:
        st.write("Sales by product")
        st.bar_chart(fdf.groupby("product_name")["gross_sales"].sum().astype(float))

    st.write("Received vs Pending by branch")
    st.bar_chart(
        fdf.groupby("branch")[["received_amount", "pending_amount"]].sum().astype(float)
    )

    st.write("Sales over time")
    daily = (
        fdf.assign(date=pd.to_datetime(fdf["date"]))
        .groupby("date")["gross_sales"].sum().astype(float)
    )
    st.line_chart(daily)
st.divider()

if st.session_state.get("flash"):
    st.success(st.session_state.pop("flash"))

# ---------- Add New Sale ----------
st.subheader("Add New Sale")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT branch_id, branch_name FROM branches")
branch_list = cursor.fetchall()
conn.close()

with st.form("add_sale_form", clear_on_submit=True):
    if user["role"] == "Super Admin":
        branch_map = {name: bid for bid, name in branch_list}
        chosen_branch = st.selectbox("Branch", list(branch_map.keys()))
        sale_branch_id = branch_map[chosen_branch]
    else:
        sale_branch_id = user["branch_id"]
        st.write("Branch: your assigned branch")

    sale_date = st.date_input("Date")
    cust_name = st.text_input("Customer name")
    mobile = st.text_input("Mobile number")
    product = st.selectbox("Product", ["DS", "DA", "BA", "FSD", "BI", "AI", "ML", "SQL"])
    gross = st.number_input("Gross sales", min_value=0.0, step=1000.0)
    add_sale = st.form_submit_button("Add Sale")

if add_sale:
    if cust_name.strip() == "" or gross <= 0:
        st.error("Enter customer name and gross sales")
    else:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO customer_sales "
                "(branch_id, date, name, mobile_number, product_name, gross_sales) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (sale_branch_id, sale_date, cust_name, mobile, product, gross)
            )
            conn.commit()
            conn.close()
            st.session_state.flash = "Sale added!"
            st.rerun()
        except mysql.connector.Error as e:
            st.error(f"Could not add sale: {e}")

# ---------- Add Payment ----------
st.subheader("Add Payment")

open_df = df[df["status"] == "Open"]

if open_df.empty:
    st.info("No open sales to add payments for.")
else:
    sale_map = {
        f"{r['sale_id']} - {r['name']} (pending ₹{float(r['pending_amount']):,.0f})":
        (int(r["sale_id"]), float(r["pending_amount"]))
        for _, r in open_df.iterrows()
    }
    with st.form("add_payment_form", clear_on_submit=True):
        chosen_sale = st.selectbox("Sale", list(sale_map.keys()))
        pay_amount = st.number_input("Amount paid", min_value=0.0, step=500.0)
        pay_date = st.date_input("Payment date")
        pay_method = st.selectbox("Payment method", ["CASH", "UPI", "CARD"])
        add_pay = st.form_submit_button("Add Payment")

    if add_pay:
        sale_id, pending = sale_map[chosen_sale]
        if pay_amount <= 0:
            st.error("Enter an amount above 0")
        elif pay_amount > pending:
            st.error(f"Amount is more than pending (₹{pending:,.0f})")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payment_splits "
                    "(sale_id, payment_date, amount_paid, payment_method) "
                    "VALUES (%s, %s, %s, %s)",
                    (sale_id, pay_date, pay_amount, pay_method)
                )
                conn.commit()
                conn.close()
                st.session_state.flash = "Payment added!"
                st.rerun()
            except mysql.connector.Error as e:
                st.error(f"Could not add payment: {e}")  
# ---------- SQL Queries ----------
st.divider()
st.subheader("SQL Queries")

queries = {
    "Q1 - All sales": """SELECT s.*
FROM customer_sales s
{where_s}""",
    "Q2 - All branches": """SELECT b.*
FROM branches b
{where_b}""",
    "Q4 - Open sales": """SELECT s.*
FROM customer_sales s
WHERE s.status = 'Open'
{and_s}""",
    "Q5 - Chennai sales": """SELECT s.*
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai'
{and_s}""",
    "Q6 - Total gross sales": """SELECT SUM(gross_sales) AS total_gross_sales
FROM customer_sales s
{where_s}""",
    "Q7 - Total received": """SELECT SUM(received_amount) AS total_received
FROM customer_sales s
{where_s}""",
    "Q8 - Total pending": """SELECT SUM(pending_amount) AS total_pending
FROM customer_sales s
{where_s}""",
    "Q9 - Sales count per branch": """SELECT b.branch_name, COUNT(*) AS total_sales
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
{where_s}
GROUP BY b.branch_name""",
    "Q11 - Sales with branch name": """SELECT s.sale_id, s.name, s.product_name, s.gross_sales, b.branch_name
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
{where_s}""",
    "Q13 - Branch-wise gross sales": """SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
{where_s}
GROUP BY b.branch_name""",
    "Q14 - Sales with payment method": """SELECT s.sale_id, s.name, s.gross_sales, p.payment_method
FROM customer_sales s
JOIN payment_splits p ON s.sale_id = p.sale_id
{where_s}""",
    "Q15 - Sales with branch admin": """SELECT s.sale_id, s.name, s.gross_sales, b.branch_name, b.branch_admin_name
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
{where_s}""",
    "Q16 - Pending above 5000": """SELECT s.*
FROM customer_sales s
WHERE s.pending_amount > 5000
{and_s}""",
    "Q17 - Top 3 gross sales": """SELECT s.*
FROM customer_sales s
{where_s}
ORDER BY s.gross_sales DESC
LIMIT 3""",
    "Q18 - Top branch by gross sales": """SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
{where_s}
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1""",
}

if user["role"] == "Super Admin":
    where_s = and_s = where_b = ""
else:
    where_s = "WHERE s.branch_id = %s"
    and_s = "AND s.branch_id = %s"
    where_b = "WHERE b.branch_id = %s"

query_choice = st.selectbox("Choose a query", list(queries.keys()))
sql = queries[query_choice].format(where_s=where_s, and_s=and_s, where_b=where_b)
sql = "\n".join(line for line in sql.splitlines() if line.strip())
st.code(sql, language="sql")

if st.button("Run query"):
    params = tuple([user["branch_id"]] * sql.count("%s"))
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchall()
        result_cols = [c[0] for c in cur.description]
        conn.close()
        st.dataframe(pd.DataFrame(result, columns=result_cols))
    except mysql.connector.Error as e:
        st.error(f"Query failed: {e}")