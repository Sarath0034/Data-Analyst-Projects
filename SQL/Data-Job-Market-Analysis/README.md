# SQL Project: Data Job Market Analysis

## Introduction

This SQL project explores the 2023 data job market to understand salary trends, in-demand skills, and the qualifications required for high-paying Data Analyst roles.

The goal is to answer real business questions using SQL queries on job posting data. The project focuses on extracting insights from relational tables, joining related data, aggregating results, and turning raw job listings into useful career insights.

## Business Questions

1. What are the highest-paying Data Analyst jobs?
2. What skills are required for the top-paying Data Analyst jobs?
3. What are the most in-demand skills for Data Analysts?
4. Which skills are associated with the highest average salaries?
5. What are the most optimal skills to learn based on both demand and salary?

## Tools Used

- PostgreSQL
- SQL
- Visual Studio Code
- Git and GitHub

## Dataset Overview

The dataset contains job postings for data-related roles. It includes information such as job title, company, salary, location, work schedule, required skills, and posting date.

### Tables Used

- `job_postings_fact`
- `company_dim`
- `skills_dim`
- `skills_job_dim`

## Project Files

| File | Analysis |
| --- | --- |
| [1_top_paying_jobs.sql](Project_SQL/1_top_paying_jobs.sql) | Finds the top-paying remote Data Analyst roles. |
| [2_top_paying_job_skills.sql](Project_SQL/2_top_paying_job_skills.sql) | Identifies skills required for the highest-paying jobs. |
| [3_top_demanded_skills.sql](Project_SQL/3_top_demanded_skills.sql) | Finds the most in-demand Data Analyst skills. |
| [4_top_paying_skills.sql](Project_SQL/4_top_paying_skills.sql) | Calculates average salary by skill. |
| [5_optimal_skills.sql](Project_SQL/5_optimal_skills.sql) | Finds skills with both strong demand and high salary potential. |

## Key Insights

- SQL remains one of the most important skills for Data Analyst roles.
- Excel, Python, Tableau, and Power BI are also highly requested skills.
- High-paying roles often require a mix of SQL, programming, visualization, and cloud/data platform skills.
- Tools such as Snowflake, Azure, AWS, BigQuery, Tableau, and Python show strong career value.
- The best skills to learn are those that combine high demand with strong salary potential.

## SQL Skills Demonstrated

- `SELECT` statements
- `WHERE` filtering
- `ORDER BY` sorting
- `GROUP BY` aggregation
- `COUNT()` and `AVG()`
- `INNER JOIN` and `LEFT JOIN`
- Common Table Expressions (CTEs)
- Subqueries
- Business problem solving with SQL

## Conclusion

This project demonstrates how SQL can be used to analyze job market data and create practical career insights. It highlights the skills, tools, and salary patterns that matter most for aspiring Data Analysts.
