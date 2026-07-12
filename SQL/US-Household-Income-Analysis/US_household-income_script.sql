#US Household Income Data Cleaning 
-- I had to convert the xlx file to a json and then import it to SQL 
-- Check the data

#PROJECT 2 PART 1 , CLEANING DATA 

SELECT * 
FROM US_Project.us_household_income_statistics;
-- If one of the labels is wrong do:
-- ALTER TABLE  US_Project.us_household_income_statistics RENAME COLUM `frnkjnerf` TO `id`

SELECT *
FROM US_Project.us_household_income;

# Lets start by counting the number of rows
SELECT COUNT(id)
FROM US_Project.us_household_income;
-- COUNT 32533

SELECT COUNT(id) 
FROM US_Project.us_household_income_statistics;
-- Count 32526

# checking waht is wrong with the data 
SELECT *
FROM US_Project.us_household_income;

SELECT * 
FROM US_Project.us_household_income_statistics;

#revising housegold income 
SELECT * 
FROM US_Project.us_household_income_statistics;

#1 removing duplicates
SELECT id, COUNT(id)
FROM US_Project.us_household_income
GROUP BY id
HAVING COUNT(id) > 1;
-- we have some duplicates , we have to delete them

DELETE FROM us_household_income
WHERE row_id IN (
	SELECT row_id
	FROM (
		SELECT row_id, id,
		ROW_NUMBER() OVER(PARTITION BY id ORDER BY id) AS row_num
		FROM US_Project.us_household_income
		) Duplicates
	WHERE row_num > 1
    );
-- 7 rows duplicated dissapear

-- Cheking the other table for duplicates
SELECT id, COUNT(id)
FROM US_Project.us_household_income_statistics
GROUP BY id
HAVING COUNT(id) > 1;
-- it doesnt have any duplicates

#2 Correcting capital letter 
SELECT *
FROM US_Project.us_household_income;

SELECT State_Name, COUNT(State_Name)
FROM US_Project.us_household_income
GROUP BY State_Name;
-- it doesnt show the low capital letter that i see

SELECT DISTINCT State_Name
FROM US_Project.us_household_income
ORDER BY 1;
-- it doesnt show it either, it seems that ut wouldnt cause a problem but i need to change the misspelled one 

UPDATE US_Project.us_household_income
SET State_Name = 'Georgia'
WHERE State_Name = 'georia';
-- I updated the misspelled one 

UPDATE US_Project.us_household_income
SET State_Name = 'Alabama'
WHERE State_Name = 'alabama'
;
-- and corrected the capital letter

#Cheching the state_ab, and it seems ok
SELECT State_ab, COUNT(State_ab)
FROM US_Project.us_household_income
GROUP BY State_ab;

SELECT DISTINCT State_ab
FROM US_Project.us_household_income
ORDER BY 1;

#Cheching place
SELECT *
FROM US_Project.us_household_income
WHERE Place = '' OR NULL;

SELECT *
FROM US_Project.us_household_income
WHERE County = 'Autauga County';

UPDATE  US_Project.us_household_income
SET Place = 'Autaugaville'
WHERE County = 'Autauga County'
AND City = 'Vinemont';
-- Populated the missing value

#Cheching type
SELECT Type, COUNT(Type)
FROM US_Project.us_household_income
GROUP BY Type;
-- It can be seen that CDP and Boroughts have isues 

UPDATE US_Project.us_household_income
SET Type = 'Borough'
WHERE Type = 'Boroughs';
-- We have merged those 

#Keep chekcing 
SELECT *
FROM US_Project.us_household_income;

SELECT Aland, AWater
FROM US_Project.us_household_income
WHERE (AWater = '' OR AWater = 0 OR AWater IS NULL)
;
-- many AWater with 0 

SELECT DISTINCT AWater
FROM US_Project.us_household_income
WHERE (AWater = '' OR AWater = 0 OR AWater IS NULL)
; 
-- just 0

SELECT Aland,AWater
FROM US_Project.us_household_income
WHERE Aland = '' OR Aland = 0 OR Aland IS NULL
;
-- Many Aland with 0

SELECT DISTINCT Aland
FROM US_Project.us_household_income
WHERE Aland = '' OR Aland = 0 OR Aland IS NULL
;
-- just 0, but not together

-- SummARY 
-- change names, remove duplicates, issues with state names, values missings 
-- Very small data cleaning 

# PROJECT 2 PART 2 

SELECT State_Name, County, City, ALand, AWater
FROM US_Project.us_household_income;
-- we can see that its interesting , and would be good to see the overll per state

#we want the largest Awater
SELECT State_Name, SUM(ALand), SUM(AWater)
FROM US_Project.us_household_income
GROUP BY State_Name
ORDER BY SUM(ALand) DESC;
-- i can write "ORDER BY 2 DESC" and it would be the same, 2 is second column
-- ALASKA IS THE BIGGEST in ALand WHICH MAKES SENSE

#we want the lasrgest Aland
SELECT State_Name, SUM(ALand), SUM(AWater)
FROM US_Project.us_household_income
GROUP BY State_Name
ORDER BY SUM(AWater) DESC;
-- ALASKA iS THE BIGGEST IN AWater

#We want the top 10 by Land
SELECT State_Name, SUM(ALand), SUM(AWater)
FROM US_Project.us_household_income
GROUP BY State_Name
ORDER BY SUM(ALand) DESC
LIMIT 10
;

#TOP 10 TEN  BY WATER 
SELECT State_Name, SUM(ALand), SUM(AWater)
FROM US_Project.us_household_income
GROUP BY State_Name
ORDER BY SUM(AWater) DESC
LIMIT 10
;

#checking the tables together, id is similar 
SELECT *
FROM US_Project.us_household_income;

SELECT * 
FROM US_Project.us_household_income_statistics;

#Joining tables through id
SELECT *
FROM US_Project.us_household_income u
JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id;
-- some of the data was missing at the beggining , which could be affect the result, lets check

SELECT *
FROM US_Project.us_household_income u
RIGHT JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE u.id IS NULL;
-- We did well importing the data 

SELECT *
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE u.id IS NULL;
-- Its still perfect 

SELECT *
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0;
-- More useful and clean data

SELECT u.State_Name, County, Type, `Primary`, Mean, Median
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0;
-- interesting and categorical data

SELECT u.State_Name, ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY u.State_Name
ORDER BY 2 DESC;
-- to see the highest or lowest by mean 

#lowest 5 
SELECT u.State_Name, ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY u.State_Name
ORDER BY 2 ASC
LIMIT 5;

#highest 10
SELECT u.State_Name, ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY u.State_Name
ORDER BY 2 DESC
LIMIT 10;

#highest by median
SELECT u.State_Name, ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY u.State_Name
ORDER BY 3 DESC
LIMIT 10;

#lowest by median 
SELECT u.State_Name, ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY u.State_Name
ORDER BY 3 ASC
LIMIT 10;

#Exploring Type
SELECT Type, ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY Type
ORDER BY 2 DESC
LIMIT 15;
-- what kind of area is wealthy, which is municipality, bbut how many?

SELECT Type, COUNT(Type), ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY Type
ORDER BY 2 DESC
LIMIT 15
;
-- not limited them, as i could miss the municipality 
-- the average is so high as its just one 
-- CPD and City could be the same

#by median
SELECT Type, COUNT(Type), ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY Type
ORDER BY 4 DESC
LIMIT 15;
-- communities is the lowest, which states are the ones

SELECT *
FROM us_household_income
WHERE Type = 'Community';
-- it shows puerto rico which makes sense

#when its soo small you might want to filter 
SELECT Type, COUNT(Type), ROUND(AVG(Mean),1), ROUND(AVG(Median),1)
FROM US_Project.us_household_income u
INNER JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
WHERE Mean <> 0
GROUP BY Type
HAVING COUNT(Type) > 100
ORDER BY 4 DESC
LIMIT 15;
-- we just filter the outliers, you need to know the data to do it, looking at the higher volumne 

#looking salaries at the city level 
SELECT u.State_Name, City, Round(AVG(Mean),1), Round(AVG(Median),1)
FROM US_Project.us_household_income u
JOIN US_Project.us_household_income_statistics us
	ON u.id = us.id
GROUP BY u.State_Name, City
ORDER BY Round(AVG(Mean),1) DESC;
-- Delta Alaska! is the highst salaries 
-- you vcan see the ones in which part of the states are 
-- The median appear as 30000 which you might need to double check.alter

-- SUMMARY
-- combining tables 
-- some dirty data with 0
-- state level high and low mean and emdian 
-- looking at types, which areas like monucipalities 
-- looking at state names and cities average incomes 
    















