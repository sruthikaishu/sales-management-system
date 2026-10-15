-- Sales Management System: database, tables and triggers
-- Run this first, then run import_data.py to load the CSV files.

CREATE DATABASE IF NOT EXISTS sales_management_system;
USE sales_management_system;

-- 1. Tables ---------------------------------------------------------------

CREATE TABLE branches (
  branch_id INT NOT NULL AUTO_INCREMENT,
  branch_name VARCHAR(100) NOT NULL,
  branch_admin_name VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (branch_id)
);

CREATE TABLE users (
  user_id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  branch_id INT DEFAULT NULL,
  role ENUM('Super Admin','Admin') NOT NULL,
  email VARCHAR(255) NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE KEY email (email),
  KEY branch_id (branch_id),
  CONSTRAINT users_ibfk_1 FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
);

CREATE TABLE customer_sales (
  sale_id INT NOT NULL AUTO_INCREMENT,
  branch_id INT NOT NULL,
  date DATE NOT NULL,
  name VARCHAR(100) NOT NULL,
  mobile_number VARCHAR(15) DEFAULT NULL,
  product_name VARCHAR(30) DEFAULT NULL,
  gross_sales DECIMAL(12,2) NOT NULL,
  received_amount DECIMAL(12,2) DEFAULT 0.00,
  pending_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
  status ENUM('Open','Close') DEFAULT 'Open',
  PRIMARY KEY (sale_id),
  UNIQUE KEY mobile_number (mobile_number),
  KEY branch_id (branch_id),
  CONSTRAINT customer_sales_ibfk_1 FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
);

CREATE TABLE payment_splits (
  payment_id INT NOT NULL AUTO_INCREMENT,
  sale_id INT NOT NULL,
  payment_date DATE NOT NULL,
  amount_paid DECIMAL(12,2) NOT NULL,
  payment_method VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (payment_id),
  KEY sale_id (sale_id),
  CONSTRAINT payment_splits_ibfk_1 FOREIGN KEY (sale_id) REFERENCES customer_sales (sale_id)
);

-- 2. Triggers -------------------------------------------------------------

DELIMITER $$

-- After a payment is added: update received amount and sale status
CREATE TRIGGER trg_payment_after_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = IFNULL(received_amount, 0) + NEW.amount_paid,
        status = CASE
            WHEN received_amount >= gross_sales THEN 'Close'
            ELSE 'Open'
        END
    WHERE sale_id = NEW.sale_id;
END$$

-- Before a sale is added: gross sales must be above 0, start as Open with 0 received
CREATE TRIGGER trg_sales_before_insert
BEFORE INSERT ON customer_sales
FOR EACH ROW
BEGIN
    IF NEW.gross_sales <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Gross sales must be greater than 0';
    END IF;
    SET NEW.received_amount = 0;
    SET NEW.status = 'Open';
END$$

DELIMITER ;
