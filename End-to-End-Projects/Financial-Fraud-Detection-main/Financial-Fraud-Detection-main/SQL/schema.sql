CREATE DATABASE financial_fraud_analytics;
USE financial_fraud_analytics;
SHOW DATABASES;
USE financial_fraud_analytics;
CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id INT,
    transaction_date DATETIME,
    transaction_type VARCHAR(50),
    channel VARCHAR(30),
    country VARCHAR(50),
    amount DECIMAL(15,2),
    is_fraud TINYINT,
    transaction_year INT,
    transaction_month INT,
    transaction_day INT,
    day_of_week INT,
    day_name VARCHAR(20),
    is_weekend TINYINT,
    is_high_value TINYINT,
    is_international TINYINT,
    is_digital TINYINT,
    is_atm TINYINT,
    log_amount DECIMAL(15,6),
    transaction_count_24h DECIMAL(15,4),
    previous_transaction_date DATETIME,
    minutes_since_previous_transaction DECIMAL(15,4),
    is_rapid_transaction TINYINT,
    amount_z_score DECIMAL(15,6),
    is_amount_anomaly TINYINT,
    risk_score INT,
    behavioural_risk_score INT
);

CREATE TABLE customer_fraud_summary (
    customer_id INT PRIMARY KEY,
    total_transactions INT,
    total_value DECIMAL(15,2),
    average_transaction_value DECIMAL(15,2),
    maximum_transaction DECIMAL(15,2),
    fraud_transactions INT,
    fraud_rate DECIMAL(10,2)
);

CREATE TABLE fraud_predictions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    fraud_probability DECIMAL(10,6),
    fraud_prediction TINYINT,
    risk_category VARCHAR(30),
    model_version VARCHAR(50),

    FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id)
);

SELECT COUNT(*) AS transaction_count
FROM transactions;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM transactions;
SET SQL_SAFE_UPDATES = 1;

SELECT COUNT(*) AS transaction_count
FROM transactions;

ALTER TABLE transactions
MODIFY COLUMN previous_transaction_date VARCHAR(30);

DESCRIBE transactions;

SELECT COUNT(*) AS transaction_count
FROM transactions;

SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT transaction_id) AS unique_transactions
FROM transactions;

SET SQL_SAFE_UPDATES = 0;
UPDATE transactions
SET previous_transaction_date = NULL
WHERE previous_transaction_date = '\\N';
SET SQL_SAFE_UPDATES = 1;
SELECT COUNT(*) AS missing_previous_dates
FROM transactions
WHERE previous_transaction_date IS NULL;
ALTER TABLE transactions
MODIFY COLUMN previous_transaction_date DATETIME NULL;
DESCRIBE transactions;
SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT transaction_id) AS unique_transactions,
    COUNT(*) -
    COUNT(previous_transaction_date)
    AS transactions_without_previous_date
FROM transactions;

SELECT
    is_fraud,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY is_fraud;
SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(is_fraud) AS fraud_transactions
FROM transactions;
