USE financial_fraud_analytics;
SELECT
    transaction_year,
    transaction_month,
    COUNT(*) AS total_transactions,
    SUM(is_fraud) AS fraud_transactions,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*),2)AS fraud_rate,
    ROUND(SUM(amount),2) AS total_transaction_value,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) AS fraudulent_transaction_value
FROM transactions
GROUP BY
    transaction_year,
    transaction_month
ORDER BY
    transaction_year,
    transaction_month;

WITH country_metrics AS (SELECT country,COUNT(*) AS total_transactions, SUM(is_fraud) AS fraud_transactions,
        ROUND(SUM(is_fraud) * 100.0 / COUNT(*),2) AS fraud_rate,
        ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END),2) AS fraudulent_value
        FROM transactions
    GROUP BY country)
SELECT
    country,
    total_transactions,
    fraud_transactions,
    fraud_rate,
    fraudulent_value,
    RANK() OVER (ORDER BY fraud_rate DESC) AS fraud_rate_rank
FROM country_metrics
ORDER BY fraud_rate_rank;

WITH channel_metrics AS (SELECT channel,COUNT(*) AS total_transactions,SUM(is_fraud) AS fraud_transactions,
SUM(amount) AS total_value,
SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) AS fraudulent_value
FROM transactions
GROUP BY channel)
SELECT
    channel,
    total_transactions,
    fraud_transactions,
    ROUND(fraud_transactions * 100.0 / total_transactions,2) AS fraud_rate,
    ROUND(total_value,2) AS total_value,
    ROUND(fraudulent_value,2) AS fraudulent_value
FROM channel_metrics
ORDER BY fraud_rate DESC;


WITH customer_metrics AS (
    SELECT customer_id,COUNT(*) AS total_transactions,SUM(is_fraud) AS fraud_transactions,
    ROUND(SUM(amount),2) AS total_transaction_value,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END),2) AS fraudulent_value
    FROM transactions
    GROUP BY customer_id)
SELECT
    customer_id,
    total_transactions,
    fraud_transactions,
    ROUND(fraud_transactions * 100.0 / total_transactions,2) AS fraud_rate,
    total_transaction_value,
    fraudulent_value,
    RANK() OVER (ORDER BY fraudulent_value DESC) AS fraud_value_rank
FROM customer_metrics
ORDER BY fraud_value_rank
LIMIT 25;

-- STEP 36 — Repeat fraud customers

WITH repeat_fraud_customers AS (
    SELECT
        customer_id,
        COUNT(*) AS fraud_transactions,
        SUM(amount) AS fraudulent_value,
        AVG(amount) AS average_fraud_amount,
        MAX(amount) AS largest_fraud_amount
FROM transactions WHERE is_fraud = 1 GROUP BY customer_id HAVING COUNT(*) >= 2)
SELECT
    customer_id,
    fraud_transactions,
    ROUND(fraudulent_value,2) AS fraudulent_value,
    ROUND(average_fraud_amount,2) AS average_fraud_amount,
    ROUND(largest_fraud_amount,2) AS largest_fraud_amount,
    RANK() OVER (ORDER BY fraudulent_value DESC) AS fraud_exposure_rank
FROM repeat_fraud_customers
ORDER BY fraud_exposure_rank;

WITH customer_velocity AS (
    SELECT
        customer_id,
        COUNT(*) AS total_transactions,
        COUNT(DISTINCT DATE(transaction_date))
            AS active_days,
        SUM(amount) AS total_transaction_value,
        AVG(transaction_count_24h)AS average_24h_transaction_count,MAX(transaction_count_24h)AS maximum_24h_transaction_count
    FROM transactions
    GROUP BY customer_id)
SELECT
    customer_id,
    total_transactions,
    active_days,
    ROUND(total_transaction_value,2) AS total_transaction_value,
    ROUND(average_24h_transaction_count,2) AS average_24h_transaction_count, maximum_24h_transaction_count,
    RANK() OVER (ORDER BY maximum_24h_transaction_count DESC) AS velocity_rank
FROM customer_velocity
ORDER BY velocity_rank
LIMIT 25;

SELECT is_rapid_transaction, COUNT(*) AS total_transactions,SUM(is_fraud) AS fraud_transactions,
ROUND(SUM(is_fraud) * 100.0/ COUNT(*),2) AS fraud_rate,
ROUND(SUM(amount),2) AS total_transaction_value,
ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END),2) AS fraudulent_value
FROM transactions
GROUP BY is_rapid_transaction
ORDER BY is_rapid_transaction DESC;

SELECT behavioural_risk_score,
    COUNT(*) AS total_transactions,
    SUM(is_fraud) AS fraud_transactions,
    ROUND(SUM(is_fraud) * 100.0/ COUNT(*),2) AS fraud_rate,
    ROUND(AVG(amount),2) AS average_transaction_amount,
    ROUND(SUM(amount),2) AS total_transaction_value,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END),2) AS fraudulent_value
FROM transactions
GROUP BY behavioural_risk_score
ORDER BY behavioural_risk_score;

WITH customer_fraud AS (SELECT customer_id,SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) AS fraudulent_value
    FROM transactions
    GROUP BY customer_id),ranked_customers AS (
    SELECT
        customer_id,
        fraudulent_value,
        RANK() OVER (ORDER BY fraudulent_value DESC) AS fraud_rank,
        SUM(fraudulent_value) OVER ()AS total_fraudulent_value
            FROM customer_fraud)
SELECT
    customer_id,
    ROUND(fraudulent_value,2) AS fraudulent_value,
    fraud_rank,ROUND(fraudulent_value * 100.0/ NULLIF(total_fraudulent_value,0),2) AS percentage_of_total_fraud_value
FROM ranked_customers
WHERE fraudulent_value > 0
ORDER BY fraud_rank
LIMIT 25;

DROP TABLE IF EXISTS customer_ml_features;
CREATE TABLE customer_ml_features AS
SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT DATE(transaction_date))
        AS active_days,
    SUM(amount) AS total_transaction_value,
    AVG(amount) AS average_transaction_amount,
    MAX(amount) AS maximum_transaction_amount,
    SUM(is_fraud) AS historical_fraud_transactions,
    AVG(is_fraud) AS historical_fraud_rate,
    AVG(transaction_count_24h)
        AS average_transaction_velocity,
    MAX(transaction_count_24h)
        AS maximum_transaction_velocity,
    SUM(is_rapid_transaction)
        AS rapid_transaction_count,
    SUM(is_amount_anomaly)
        AS amount_anomaly_count,
    SUM(is_international)
        AS international_transaction_count,
    SUM(is_digital)
        AS digital_transaction_count, AVG(behavioural_risk_score) AS average_behavioural_risk_score, MAX(behavioural_risk_score) AS maximum_behavioural_risk_score
FROM transactions
GROUP BY customer_id;

SELECT
    COUNT(*) AS customer_count
FROM customer_ml_features;

SELECT *
FROM customer_ml_features
LIMIT 10;
USE financial_fraud_analytics;
SELECT *
FROM customer_ml_features;