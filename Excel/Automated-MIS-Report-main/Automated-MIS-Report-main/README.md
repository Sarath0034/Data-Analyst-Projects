# Automated MIS Reporting & Performance Dashboard

## 📌 Project Overview

This project demonstrates an end-to-end **MIS Reporting Automation Solution** developed using **Microsoft Excel, Power Query, PivotTables, PivotCharts, and Excel formulas**.

The primary objective of this project was to automate repetitive operational reporting activities such as **data loading, data cleaning, data transformation, data consolidation, KPI calculation, exception identification, and report formatting**.

The solution transforms recurring raw operational files into a structured and management-ready MIS report with minimal manual intervention.

---

## 🎯 Business Problem

In a traditional MIS reporting process, operational files need to be manually:

- Collected from different sources
- Cleaned and standardized
- Checked for data-quality issues
- Consolidated with historical data
- Calculated for productivity and SLA metrics
- Converted into reports
- Formatted before sharing with management

Performing these activities manually on a recurring basis is **time-consuming, repetitive, and prone to human errors**.

### Objective

The objective was to build an automated reporting workflow that could:

1. Load recurring operational files.
2. Clean and validate raw data.
3. Standardize data formats.
4. Handle duplicate and inconsistent records.
5. Identify missing values and outliers.
6. Append new data with historical data.
7. Calculate operational KPIs.
8. Generate structured MIS reports.
9. Automate repetitive Excel tasks using VBA.
10. Provide management with an interactive dashboard.

---

# 🔄 End-to-End MIS Workflow

```text
                Source Files
                     │
                     ▼
              Data Ingestion
                     │
                     ▼
                Power Query
                     │
                     ▼
            Data Cleaning
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Data Types    Duplicates    Text
    Validation    Handling      Standardization
        │            │            │
        └────────────┼────────────┘
                     ▼
             Missing Values
                     │
                     ▼
             Outlier Detection
                     │
                     ▼
           Data Transformation
                     │
                     ▼
        Historical + Current Data
                  Append
                     │
                     ▼
             KPI Calculations
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   Productivity      SLA        Error Rate
        │            │             │
        └────────────┼─────────────┘
                     ▼
              Master Dataset
                     │
                     ▼
             PivotTables &
              PivotCharts
                     │
                     ▼
            MIS Dashboard
                     │
                     ▼
             VBA Automation
                     │
                     ▼
          Management Reporting

```
---

# 📷 Dashboard Preview

<img width="1122" height="560" alt="image" src="https://github.com/user-attachments/assets/c5ef798a-26c1-4901-b3ea-0971f6ee6d52" />
