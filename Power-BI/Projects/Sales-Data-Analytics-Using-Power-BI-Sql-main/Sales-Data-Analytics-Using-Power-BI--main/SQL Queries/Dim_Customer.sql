
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