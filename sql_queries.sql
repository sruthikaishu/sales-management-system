-- Q1
SELECT * FROM customer_sales;

-- Q2
SELECT * FROM branches;

-- Q4
SELECT * FROM customer_sales WHERE status = 'Open';

-- Q5
SELECT s.*
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';

-- Q6
SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;

-- Q7
SELECT SUM(received_amount) AS total_received FROM customer_sales;

-- Q8
SELECT SUM(pending_amount) AS total_pending FROM customer_sales;

-- Q9
SELECT b.branch_name, COUNT(*) AS total_sales
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name;

-- Q11
SELECT s.sale_id, s.name, s.product_name, s.gross_sales, b.branch_name
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id;

-- Q13
SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name;

-- Q14
SELECT s.sale_id, s.name, s.gross_sales, p.payment_method
FROM customer_sales s
JOIN payment_splits p ON s.sale_id = p.sale_id;

-- Q15
SELECT s.sale_id, s.name, s.gross_sales, b.branch_name, b.branch_admin_name
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id;

-- Q16
SELECT * FROM customer_sales WHERE pending_amount > 5000;

-- Q17
SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;

-- Q18
SELECT b.branch_name, SUM(s.gross_sales) AS total_gross_sales
FROM customer_sales s
JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;