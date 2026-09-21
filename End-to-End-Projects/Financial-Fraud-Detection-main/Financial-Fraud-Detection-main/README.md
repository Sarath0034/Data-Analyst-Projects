# Financial Fraud Detection & Transaction Intelligence

## Project Overview

An end-to-end financial fraud analytics project combining **Python, SQL, Machine Learning, anomaly detection, and Power BI** to analyse transaction behaviour, identify suspicious activity, estimate fraud risk, and support fraud-investigation workflows.

The project demonstrates a complete workflow from raw transaction data through data preparation, advanced SQL analysis, predictive modelling, risk scoring, and an operational Power BI dashboard.

## Business Problem

Financial institutions process large volumes of transactions, making manual identification of suspicious activity difficult.

This project addresses questions such as:

- What is the overall fraud rate?
- Which countries and transaction channels have the highest fraud exposure?
- Which customers demonstrate repeated or unusual behaviour?
- Are rapid transactions associated with higher fraud risk?
- Which transaction amounts behave like statistical anomalies?
- Can machine learning estimate fraud probability?
- Which transactions should be prioritised for investigation?
- How can fraud risk and financial exposure be monitored through an interactive dashboard?

## Project Objectives

1. Clean and validate transaction data.
2. Engineer behavioural and transaction-level features.
3. Analyse fraud patterns using SQL.
4. Detect unusual transaction behaviour and amount anomalies.
5. Build customer-level ML features.
6. Train and compare fraud classification models.
7. Evaluate models using fraud-appropriate metrics.
8. Optimise probability thresholds.
9. Generate transaction-level fraud probabilities and risk tiers.
10. Build a Power BI fraud-monitoring dashboard.
11. Create a priority fraud investigation queue.

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Analysis | Pandas, NumPy |
| Visualisation | Matplotlib |
| Database | MySQL |
| SQL | CTEs, aggregations, window functions |
| Machine Learning | Scikit-learn |
| Imbalanced Classification | imbalanced-learn |
| BI | Microsoft Power BI |
| Development | Jupyter Notebook / VS Code |
| Version Control | Git / GitHub |

## Dataset

The project uses a synthetic financial transaction dataset containing approximately **200,000 transactions**.

Core attributes include:

- Transaction ID
- Customer ID
- Transaction date
- Transaction type
- Channel
- Country
- Transaction amount
- Fraud label

The project additionally creates engineered behavioural features for fraud analysis and modelling.

## Project Architecture

```text
Raw Transaction Data
        |
        v
Data Quality Validation
        |
        v
Feature Engineering
        |
        +----> Time Features
        +----> Transaction Risk Features
        +----> Transaction Velocity
        +----> Amount Anomaly Detection
        |
        v
Advanced SQL Analytics
        |
        +----> Country Risk
        +----> Channel Risk
        +----> Customer Behaviour
        +----> Fraud Concentration
        +----> Customer ML Features
        |
        v
Machine Learning
        |
        +----> Logistic Regression
        +----> Random Forest
        +----> Balanced Random Forest
        |
        v
Model Evaluation
        |
        +----> Precision
        +----> Recall
        +----> F1
        +----> ROC-AUC
        +----> Precision-Recall
        +----> Threshold Analysis
        |
        v
Transaction-Level Prediction
        |
        +----> Fraud Probability
        +----> Risk Category
        +----> Potential Exposure
        |
        v
Power BI
        |
        +----> Executive KPIs
        +----> Risk Distribution
        +----> Fraud Trends
        +----> Country Analysis
        +----> Channel Analysis
        +----> Investigation Queue
```

## 1. Data Preparation & Feature Engineering

Python was used to inspect data quality, convert transaction dates, and create analytical features.

Features include:

- Transaction year, month and day
- Day of week and weekend indicator
- High-value transaction indicator
- International transaction indicator
- Digital transaction indicator
- ATM transaction indicator
- Log-transformed transaction amount
- Customer transaction frequency
- 24-hour transaction velocity
- Time since previous transaction
- Rapid transaction indicator
- Transaction amount Z-score
- Amount anomaly indicator
- Composite risk score
- Behavioural risk score

## 2. Anomaly Detection

Statistical anomaly detection was applied to transaction amounts using a Z-score.

Transactions with:

```text
|Z-score| >= 3
```

were flagged as amount anomalies.

The analysis compared anomalous and normal transactions in terms of transaction volume, fraud volume, average amount, maximum amount and fraud rate.

## 3. MySQL Data Warehouse

A MySQL database named:

```text
financial_fraud_analytics
```

was created.

Core tables include:

```text
transactions
customer_fraud_summary
customer_ml_features
fraud_predictions
```

The transaction table stores engineered transaction-level features.

Data integrity checks included:

- Total transaction count
- Unique transaction IDs
- Unique customers
- Fraud transaction count
- Missing customer IDs
- Invalid amounts
- Missing previous transaction dates

The final transaction table contains **200,000 transactions** with **200,000 unique transaction IDs**.

## 4. Advanced SQL Analytics

SQL analysis was used to identify:

- Monthly fraud trends
- Country-level fraud risk
- Channel-level fraud exposure
- Customer fraud behaviour
- Repeat fraud customers
- Fraud concentration
- Transaction velocity
- Behavioural risk-score effectiveness

The SQL layer demonstrates:

- `GROUP BY`
- `CASE`
- `HAVING`
- Conditional aggregation
- Common Table Expressions (CTEs)
- `RANK()`
- Window functions
- Customer-level feature aggregation

## 5. Customer-Level Machine Learning Dataset

A customer-level ML feature table was created in MySQL and exported to Python.

Features include:

```text
total_transactions
active_days
total_transaction_value
average_transaction_amount
maximum_transaction_amount
average_transaction_velocity
maximum_transaction_velocity
rapid_transaction_count
amount_anomaly_count
international_transaction_count
digital_transaction_count
average_behavioural_risk_score
maximum_behavioural_risk_score
```

The modelling target was:

```text
1 = customer has historical fraudulent activity
0 = customer has no historical fraudulent activity
```

Direct target-derived fields such as historical fraud count and historical fraud rate were excluded from the predictive feature set to reduce target leakage.

## 6. Machine Learning Models

Three classification approaches were trained:

### Logistic Regression

Used as an interpretable baseline with balanced class weighting.

### Random Forest

A nonlinear ensemble model using:

- 300 estimators
- Maximum depth of 12
- Minimum samples split of 10
- Minimum samples leaf of 5
- Balanced class weights

### Balanced Random Forest

Used as an additional minority-class-focused approach for the imbalanced fraud classification problem.

## 7. Model Evaluation

Models were evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

Precision and recall were prioritised alongside F1 and ROC-AUC because fraud detection is an imbalanced classification problem.

## 8. Model Explainability

Random Forest feature importance was calculated for both customer-level and transaction-level models.

The results were visualised using Matplotlib to understand which behavioural and transaction features contributed most strongly to model decisions.

## 9. Threshold Optimisation

Fraud probability thresholds from **0.10 to 0.90** were evaluated using:

- Precision
- Recall
- F1 Score

The threshold producing the highest F1 score was identified as an analytical candidate.

In a production environment, the final threshold would also consider fraud-loss costs, false-positive investigation costs, customer friction, investigation capacity and regulatory requirements.

## 10. Transaction-Level Fraud Prediction

A dedicated transaction-level Random Forest was trained using features including:

```text
amount
is_high_value
is_international
is_digital
is_atm
transaction_count_24h
minutes_since_previous_transaction
is_rapid_transaction
amount_z_score
is_amount_anomaly
risk_score
behavioural_risk_score
is_weekend
```

The model generates:

```text
fraud_probability
model_prediction
risk_category
```

## 11. Fraud Risk Categories

Transactions were grouped into analytical risk tiers:

| Fraud Probability | Risk Category |
|---:|---|
| 0–25% | Low Risk |
| 25–50% | Medium Risk |
| 50–75% | High Risk |
| 75–100% | Critical Risk |

These are portfolio-level analytical categories and are not intended to represent regulatory or production fraud-decision thresholds.

## 12. Fraud Investigation Queue

A transaction-level investigation queue contains:

- Transaction ID
- Customer ID
- Transaction date
- Transaction type
- Channel
- Country
- Amount
- Fraud probability
- Risk category
- Potential exposure

The dashboard prioritises **High Risk** and **Critical Risk** transactions.

## 13. Power BI Dashboard

The final Power BI dashboard provides executive and operational fraud monitoring.

### Executive KPIs

- Total Transactions
- Actual Fraud Transactions
- Fraud Rate
- Fraudulent Transaction Value
- Potential Exposure

### Risk Distribution

A donut chart shows Low, Medium, High and Critical risk transactions.

### Fraud Trends

Daily fraud transaction and potential exposure trends are displayed.

### Channel Analysis

Fraudulent transaction value is analysed by channel.

### Country Analysis

Fraudulent transaction value is analysed by country.

### Investigation Queue

A detailed table highlights high-risk and critical-risk transactions for investigation.

## 14. Key Business Questions Answered

1. How many transactions are being processed?
2. What percentage are fraudulent?
3. What is the financial value of fraudulent transactions?
4. Which channels have the highest fraud exposure?
5. Which countries have the highest fraud exposure?
6. Which customers demonstrate repeated fraudulent activity?
7. Are rapid transactions associated with increased fraud?
8. Which transactions are statistical amount anomalies?
9. Which features contribute most to fraud predictions?
10. Which transactions should investigators prioritise?
11. How much potential financial exposure exists within high-risk transactions?
12. How can fraud risk be monitored over time?

## 15. Project Outputs

```text
Dataset/
├── Raw/
└── Processed/
    ├── financial_transactions_processed.csv
    ├── customer_ml_features.csv
    ├── fraud_transaction_predictions.csv
    ├── daily_fraud_monitoring.csv
    └── fraud_model_feature_importance.csv

SQL/
├── schema.sql
└── business_queries.sql

Notebooks/
└── Fraud_Detection_ML.ipynb

PowerBI/
└── Financial_Fraud_Detection_Intelligence.pbix

Models/

README.md
```

## 16. Skills Demonstrated

### Data Analytics
- Exploratory Data Analysis
- Data Cleaning
- Data Validation
- Feature Engineering
- Behavioural Analytics
- KPI Development
- Business Risk Analysis

### SQL
- MySQL
- CTEs
- Window Functions
- Ranking
- Conditional Aggregation
- Analytical Queries
- Customer-Level Aggregation

### Machine Learning
- Binary Classification
- Logistic Regression
- Random Forest
- Balanced Random Forest
- Class Imbalance
- Feature Importance
- ROC-AUC
- Precision
- Recall
- F1 Score
- Precision-Recall Analysis
- Threshold Optimisation

### Anomaly Detection
- Z-score analysis
- Transaction amount anomalies
- Transaction velocity
- Rapid transaction detection

### Business Intelligence
- Power BI
- DAX
- KPI dashboards
- Risk segmentation
- Trend analysis
- Operational investigation dashboards

## 17. Portfolio Value

This project demonstrates an end-to-end analytical workflow rather than only a machine-learning model.

It combines:

```text
Data Engineering
      +
SQL Analytics
      +
Statistical Analysis
      +
Machine Learning
      +
Risk Modelling
      +
Business Intelligence
```

The result is a practical fraud analytics solution that moves from raw transaction data to risk identification, predictive scoring, financial exposure analysis and investigation workflows.

## Author

**Keerthi Shrinivas Mungal**

Data Analyst | Data Science | Machine Learning | Business Intelligence

## Disclaimer

This project uses synthetic transaction data and is intended for educational, portfolio and demonstration purposes. It is not a production fraud-detection system and should not be used for real financial decisions without appropriate validation, governance, security, regulatory review and model-risk controls.
