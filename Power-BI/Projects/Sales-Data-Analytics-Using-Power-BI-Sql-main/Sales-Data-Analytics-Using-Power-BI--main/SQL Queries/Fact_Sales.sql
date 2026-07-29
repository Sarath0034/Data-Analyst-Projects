
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