# Sales Intelligence Hub

A sales management system for a company with 8 branches. Data is stored in **MySQL** and shown through a **Streamlit** web app written in **Python**.

## Features

- Login with two roles: **Super Admin** (all branches) and **Admin** (own branch only)
- Dashboard with Total Sales, Received and Pending amounts
- Sales table with filters: branch, product, start date, end date
- Add New Sale form
- Add Payment form (amount cannot be more than the pending amount)
- Reports: sales by branch, sales by product, received vs pending, sales over time
- SQL Queries section that runs 15 project queries inside the app
- Two MySQL triggers that keep received amount and status correct

## Tech stack

| Tool | Use |
|---|---|
| MySQL | Database, triggers, SQL queries |
| Python | Application logic |
| Streamlit | Web interface |
| pandas | Data handling and CSV import |
| mysql-connector-python | Python to MySQL connection |

## Database design

Database name: `sales_management_system`

| Table | Purpose | Key columns |
|---|---|---|
| `branches` | The 8 branches | `branch_id` (PK), `branch_name`, `branch_admin_name` |
| `users` | Logins | `user_id` (PK), `username`, `password`, `branch_id` (FK), `role`, `email` |
| `customer_sales` | Every sale | `sale_id` (PK), `branch_id` (FK), `date`, `name`, `mobile_number`, `product_name`, `gross_sales`, `received_amount`, `pending_amount`, `status` |
| `payment_splits` | Every payment | `payment_id` (PK), `sale_id` (FK), `payment_date`, `amount_paid`, `payment_method` |

Relationships: one branch has many users and many sales. One sale has many payments.
`pending_amount` is a stored generated column. The Super Admin has no branch (`branch_id` is NULL).

## Triggers

1. `trg_payment_after_insert` (on `payment_splits`, AFTER INSERT): adds the payment to `received_amount` and sets the sale status to Close when it is fully paid, otherwise Open.
2. `trg_sales_before_insert` (on `customer_sales`, BEFORE INSERT): rejects a sale if gross sales is 0 or less, and starts every new sale with received amount 0 and status Open.

## How to run

1. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
2. Create the database, tables and triggers in MySQL (see `schema.sql`).
3. Put the four CSV files in the same folder as `import_data.py` and load the data:
   ```
   python import_data.py
   ```
   This clears the old data first, then loads: 8 branches, 9 users, 1000 sales, 2011 payments.
4. Set your own MySQL user and password in `get_connection()` in `app.py` and `import_data.py`.
5. Start the app:
   ```
   streamlit run app.py
   ```
   Open http://localhost:8501

## Demo logins

| Username | Password | Role | Sees |
|---|---|---|---|
| `superadmin` | `super123` | Super Admin | All branches |
| `admin_chennai` | `admin123` | Admin | Chennai |
| `admin_bangalore` | `admin123` | Admin | Bangalore |
| `admin_hyderabad` | `admin123` | Admin | Hyderabad |
| `admin_delhi` | `admin123` | Admin | Delhi |
| `admin_mumbai` | `admin123` | Admin | Mumbai |
| `admin_pune` | `admin123` | Admin | Pune |
| `admin_kolkata` | `admin123` | Admin | Kolkata |
| `admin_ahmedabad` | `admin123` | Admin | Ahmedabad |

These are demo logins for the sample data only.

## SQL queries

The 15 queries are in `sql_queries.sql`:

| Group | Queries |
|---|---|
| Basic | Q1, Q2, Q4, Q5 |
| Aggregation | Q6, Q7, Q8, Q9 |
| Join | Q11, Q13, Q14, Q15 |
| Financial | Q16, Q17, Q18 |

Sample results: total gross sales 36,768,000, total received 19,028,113, total pending 17,739,887. Kolkata has the highest gross sales (5,101,000).

## Project files

| File | Purpose |
|---|---|
| `app.py` | Streamlit application |
| `import_data.py` | Clears the tables and loads the CSV files |
| `sql_queries.sql` | The 15 SQL queries |
| `schema.sql` | Tables and triggers |
| `branches.csv`, `users.csv`, `customer_sales.csv`, `payment_splits.csv` | Sample data |
| `requirements.txt` | Python libraries |

## Possible improvements

- Store passwords as hashes instead of plain text
- Split `app.py` into separate modules (database, login, pages)
- Move the database settings into environment variables

## Author

Sruthika
