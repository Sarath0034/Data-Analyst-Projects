
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