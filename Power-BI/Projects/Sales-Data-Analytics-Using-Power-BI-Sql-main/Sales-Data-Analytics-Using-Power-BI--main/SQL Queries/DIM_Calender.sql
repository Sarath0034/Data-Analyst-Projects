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