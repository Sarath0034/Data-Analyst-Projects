# Sales-Data-Analytics-Using-Power-BI

## Project Overview 

The **Sales Analytics Dashboard** is an interactive Power BI report designed to provide insights into the sales performance of a fictional internet sales. 

This project utilizes the AdventureWorks sample database, which contains relevant business scenarios and data. The project involved data modeling, cleansing, and transformation to create a comprehensive dashboard for business user analysis. 

## Architecture Overview 

![Architecture Overview](https://github.com/RajkumarManala1/Sales-Data-Analytics-Using-Power-BI-/blob/main/Screenshots%20of%20projects/Architecture%20Overview.png?raw=true)

### Data Loading and Transformation 
The data was imported into SQL Server using SQL Server Management Studio (SSMS), where various transformations were applied using T-SQL and Power Query Editor.

### Data Visualization
Power BI is utilized to create a comprehensive visualization dashboard that provides critical business insights and an overview of key performance indicators. This enables stakeholders to make informed decisions based on real-time data analysis.


### SQL Queries

#### Cleansed Fact_Sales Table

The following SQL query selects relevant columns from the cleansed **Fact_Sales** table, filtering for sales data from the last three years:

```sql

SELECT 
  [ProductKey],                -- Unique identifier for the product
  [OrderDateKey],              -- Key representing the date of the order
  [DueDateKey],                -- Key representing the due date for the order
  [ShipDateKey],               -- Key representing the shipping date of the order
  [CustomerKey],               -- Unique identifier for the customer
  [SalesOrderNumber],          -- Unique identifier for the sales order
  [SalesAmount]                -- Total sales amount for the order
FROM 
  [AdventureWorksDW2022].[dbo].[FactInternetSales]  -- Specify the source table in the AdventureWorksDW2022 database
WHERE 
  LEFT(OrderDateKey, 4) >= YEAR(GETDATE()) - 3   -- Filter to include orders from the last two years
ORDER BY
  OrderDateKey ASC;               -- Order the results by the order date in ascending order
```

#### Cleansed Dim_Customers Table

The following SQL query selects relevant columns from the cleansed **Dim_Customers** table, providing customer details along with their associated city information:

```sql

SELECT 
  c.CustomerKey AS CustomerKey,                               -- Unique identifier for the customer
  c.FirstName AS [First Name],                                -- Customer's first name
  c.LastName AS [Last Name],                                  -- Customer's last name
  c.FirstName + ' ' + c.LastName AS [Full Name],            -- Full name derived from first and last names
  CASE c.Gender WHEN 'M' THEN 'Male' WHEN 'F' THEN 'Female' END AS Gender,  -- Cleaning gender information
  c.DateFirstPurchase AS DateFirstPurchase,                  -- Date of the customer's first purchase
  g.City AS [Customer City]                                   -- Joined customer city from Geography table
FROM 
  [AdventureWorksDW2019].[dbo].[DimCustomer] AS c           -- Specify the source table for customer data
  LEFT JOIN dbo.DimGeography AS g ON g.GeographyKey = c.GeographyKey  -- Left join to include geography data
ORDER BY 
  CustomerKey ASC;                                          -- Order the results by CustomerKey in ascending order
```

#### Cleansed Dim_Calendar Table

The following SQL query selects relevant columns from the cleansed **Dim_Calendar** table, providing date-related information for the years 2020 and onward:

```sql
SELECT 
  [DateKey],                                -- Unique identifier for the date
  [FullDateAlternateKey] AS Date,           -- Full date in alternate format
  [EnglishDayNameOfWeek] AS Day,            -- Day of the week in English
  [EnglishMonthName] AS Month,               -- Month name in English
  LEFT([EnglishMonthName], 3) AS MonthShort, -- Shortened month name (first three letters)
  [MonthNumberOfYear] AS MonthNo,          -- Numeric representation of the month
  [CalendarQuarter] AS Quarter,             -- Quarter of the calendar year
  [CalendarYear] AS Year                    -- Year
FROM 
  [AdventureWorksDW2022].[dbo].[DimDate]   -- Specify the source table in the AdventureWorksDW2022 database
WHERE 
  CalendarYear >= 2019;                     -- Filter to include records from the year 2020 onward
```

#### Cleansed Dim_Products Table

The following SQL query selects relevant columns from the cleansed **Dim_Products** table, providing detailed information about each product along with its associated category and subcategory:

```sql

SELECT 
  p.ProductKey,                                        -- Unique identifier for the product
  p.ProductAlternateKey AS ProductItemCode,          -- Alternate key for product item code
  p.EnglishProductName AS [Product Name],             -- Name of the product in English
  ps.EnglishProductSubcategoryName AS [Sub Category],  -- Subcategory of the product (joined from Sub Category Table)
  pc.EnglishProductCategoryName AS [Product Category], -- Category of the product (joined from Category Table)
  p.Color AS [Product Color],                          -- Color of the product
  p.Size AS [Product Size],                            -- Size of the product
  p.ProductLine AS [Product Line],                    -- Line the product belongs to
  p.ModelName AS [Product Model Name],                -- Model name of the product
  p.EnglishDescription AS [Product Description],      -- Description of the product in English
  ISNULL(p.Status, 'Outdated') AS [Product Status]    -- Status of the product (default to 'Outdated' if NULL)
FROM 
  [AdventureWorksDW2022].[dbo].[DimProduct] AS p     -- Specify the source table for product data
  LEFT JOIN dbo.DimProductSubcategory AS ps ON ps.ProductSubcategoryKey = p.ProductSubcategoryKey  -- Left join to include product subcategory data
  LEFT JOIN dbo.DimProductCategory AS pc ON ps.ProductCategoryKey = pc.ProductCategoryKey       -- Left join to include product category data
ORDER BY 
  p.ProductKey ASC;                                   -- Order the results by ProductKey in ascending order
```



## Power Query Transformations

After cleansing the data in SQL Server, further transformations were performed in the **Power Query Editor**. The following transformations were applied to enhance the data quality and structure:

- **Removing columns and rows**: Unnecessary columns and rows were eliminated to streamline the dataset.
- **Filtering data**: Specific criteria were used to filter the data for more relevant insights.
- **Replacing values**: Certain values were replaced to ensure consistency across the dataset.
- **Changing data types**: Data types were adjusted to align with analytical requirements and improve performance.
- **Splitting and merging columns**: Columns were split or merged as needed to facilitate analysis and reporting.
- **Removing duplicates**: Duplicate entries were identified and removed to maintain data integrity.
- **Performing date and time transformations**: Date and time formats were standardized for better usability in reporting and analysis.

These transformations ensured that the data was well-prepared for visualization and analysis in Power BI.

## Building the Power BI Dashboard

After completing the data transformations, the data was loaded into Power BI. Four key measures were created using DAX:

```
Budget Amount = SUM(FACT_Budget[Budget])

Sales = SUM(FACT_Sales[SalesAmount])

Sales - Budget = [Sales] - [Budget Amount]

Sales / Budget Amount = DIVIDE([Sales], [Budget Amount])
```

These measures allow for insightful calculations regarding budget and sales performance.

### Star Schema Model

A **star schema** was constructed in the model view, connecting the facts and dimensions tables, which facilitates efficient reporting and analysis.

![Star Schema Model](https://github.com/RajkumarManala1/Sales-Data-Analytics-Using-Power-BI-/blob/main/Screenshots%20of%20projects/Schema.png?raw=true)

### Dashboards Created

#### Sales Overview Dashboard
- **Description**: Provides insights into overall sales performance, trends, and comparisons against budgets.

![Sales Overview Dashboard](https://github.com/RajkumarManala1/Sales-Data-Analytics-Using-Power-BI-/blob/main/Screenshots%20of%20projects/Sales%20Overview.png?raw=true)

**Comments**: The Sales Overview dashboard allows users to visualize key performance indicators (KPIs) and trends, facilitating quick decision-making regarding sales strategies.

---

#### Customer Details Dashboard
- **Description**: Displays detailed customer information, including demographics and purchasing behavior.

![Customer Details Dashboard](https://github.com/RajkumarManala1/Sales-Data-Analytics-Using-Power-BI-/blob/main/Screenshots%20of%20projects/Customer%20Overview.png?raw=true)

**Comments**: This dashboard enables businesses to understand their customer base better and tailor marketing efforts based on customer profiles.

---

#### Product Details Dashboard
- **Description**: Showcases product performance metrics, including sales by product category and subcategory.

![Product Details Dashboard](https://github.com/RajkumarManala1/Sales-Data-Analytics-Using-Power-BI-/blob/main/Screenshots%20of%20projects/Product%20Overview.png?raw=true)

**Comments**: The Product Details dashboard provides insights into which products are performing well, assisting in inventory and marketing decisions.

---

### Technologies Used

This project utilizes the following technologies:

- **Microsoft SQL Server**
- **T-SQL**
- **SQL Server Management Studio (SSMS)**
- **Power Query Editor**
- **Power BI**
- **DAX**


### Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any improvements or suggestions.

