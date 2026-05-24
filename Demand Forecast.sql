IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'PortfolioDB')
BEGIN
    CREATE DATABASE PortfolioDB;
END
GO

USE PortfolioDB;
GO

IF OBJECT_ID('dbo.', 'U') IS NOT NULL
    DROP TABLE dbo.Demand_Forecast;
GO

CREATE TABLE dbo.Demand_Forecast (
    Record_ID INT PRIMARY KEY IDENTITY(1,1),
    Date DATE NOT NULL,
    Product VARCHAR(50),
    Units_Sold INT,
    Unit_Price DECIMAL(10,2),
    Is_Holiday INT
);
GO

SELECT * FROM dbo.Demand_Forecast;
GO

-- Count total number of records to verify data ingestion
SELECT COUNT(*) AS Total_Records 
FROM dbo.Demand_Forecast;
GO

-- Check the historical range to ensure 2 years of data coverage
SELECT MIN(Date) AS Start_Date, MAX(Date) AS End_Date 
FROM dbo.Demand_Forecast;
GO

-- Aggregate sales volume by product
SELECT Product, COUNT(*) AS Record_Count, SUM(Units_Sold) AS Total_Units 
FROM dbo.Demand_Forecast 
GROUP BY Product;
GO

-- Analyze demand metrics (Average and Peak) per product
SELECT Product, AVG(Units_Sold) AS Average_Daily_Demand, MAX(Units_Sold) AS Peak_Demand 
FROM dbo.Demand_Forecast 
GROUP BY Product;
GO

-- Compare demand distribution between Holiday and Non-Holiday days
SELECT Is_Holiday, COUNT(*) AS Total_Days, AVG(Units_Sold) AS Avg_Demand 
FROM dbo.Demand_Forecast 
GROUP BY Is_Holiday;
GO

-- Retrieve top 10 high-performance sales days
SELECT TOP 10 * FROM dbo.Demand_Forecast 
ORDER BY Units_Sold DESC;
GO

-- Calculate average unit pricing for product strategy
SELECT Product, AVG(Unit_Price) AS Average_Price 
FROM dbo.Demand_Forecast 
GROUP BY Product;
GO

-- Monthly demand trend analysis
SELECT FORMAT(Date, 'yyyy-MM') AS Month, SUM(Units_Sold) AS Monthly_Total_Units
FROM dbo.Demand_Forecast
GROUP BY FORMAT(Date, 'yyyy-MM')
ORDER BY Month;
GO

-- Calculate total revenue per product (Business Metric)
SELECT Product, SUM(Units_Sold * Unit_Price) AS Total_Revenue
FROM dbo.Demand_Forecast
GROUP BY Product
ORDER BY Total_Revenue DESC;
GO

-- Identify bottom 5 products by sales volume
SELECT TOP 5 Product, SUM(Units_Sold) AS Total_Units
FROM dbo.Demand_Forecast
GROUP BY Product
ORDER BY Total_Units ASC;
GO

-- Calculate price volatility per product
SELECT Product, STDEV(Unit_Price) AS Price_Volatility
FROM dbo.Demand_Forecast
GROUP BY Product;
GO

-- Check for data quality: Identify missing or null values in critical columns
SELECT COUNT(*) AS Null_Units_Sold_Count
FROM dbo.Demand_Forecast
WHERE Units_Sold IS NULL;
GO

-- Analyze demand performance impact: Holiday vs Non-Holiday efficiency
SELECT Product, Is_Holiday, AVG(CAST(Units_Sold AS FLOAT)) AS Avg_Demand
FROM dbo.Demand_Forecast
GROUP BY Product, Is_Holiday
ORDER BY Product, Is_Holiday;
GO

-- Identify variance: Find days where sales were significantly above average per product
SELECT * FROM (
    SELECT *, AVG(Units_Sold) OVER(PARTITION BY Product) as Product_Avg
    FROM dbo.Demand_Forecast
) AS SubQuery
WHERE Units_Sold > (Product_Avg * 1.5)
ORDER BY Product, Units_Sold DESC;
GO

-- Performance trend: Compare demand between current and previous month (requires continuous dates)
SELECT 
    Product, 
    FORMAT(Date, 'yyyy-MM') AS Month,
    SUM(Units_Sold) AS Current_Month_Sales,
    LAG(SUM(Units_Sold)) OVER (PARTITION BY Product ORDER BY FORMAT(Date, 'yyyy-MM')) AS Previous_Month_Sales
FROM dbo.Demand_Forecast
GROUP BY Product, FORMAT(Date, 'yyyy-MM');
GO

-- Calculate product consistency: Coefficient of Variation (lower is more predictable)
SELECT 
    Product, 
    STDEV(Units_Sold) / NULLIF(AVG(CAST(Units_Sold AS FLOAT)), 0) AS Demand_Volatility_Index
FROM dbo.Demand_Forecast
GROUP BY Product
ORDER BY Demand_Volatility_Index ASC;
GO

------------------------------------------------------

USE PortfolioDB;
GO

IF OBJECT_ID('dbo.Demand_Predictions', 'U') IS NOT NULL
    DROP TABLE dbo.Demand_Predictions;
GO

CREATE TABLE dbo.Demand_Predictions (
    Prediction_ID INT PRIMARY KEY IDENTITY(1,1),
    Date DATE,
    Product VARCHAR(50),
    Predicted_Units INT,
    Execution_Date DATETIME DEFAULT GETDATE()
);
GO

-- Verify if the prediction process has populated data
SELECT TOP 10 * FROM dbo.Demand_Predictions;
GO

-- Check the forecast horizon (start and end dates of predictions)
SELECT MIN(Date) AS Forecast_Start, MAX(Date) AS Forecast_End 
FROM dbo.Demand_Predictions;
GO

-- Count predictions generated per product to ensure model coverage
SELECT Product, COUNT(*) AS Prediction_Count 
FROM dbo.Demand_Predictions 
GROUP BY Product;
GO

-- Calculate the volume of predicted units per product
SELECT Product, SUM(Predicted_Units) AS Total_Predicted_Units 
FROM dbo.Demand_Predictions 
GROUP BY Product 
ORDER BY Total_Predicted_Units DESC;
GO

-- Identify specific predicted dates for a chosen product
SELECT Date, Predicted_Units 
FROM dbo.Demand_Predictions 
WHERE Product = 'HP Laptop' 
ORDER BY Date ASC;
GO

-- Identify duplicate predictions for the same product and date (Integrity check)
SELECT Date, Product, COUNT(*) AS Occurrences
FROM dbo.Demand_Predictions
GROUP BY Date, Product
HAVING COUNT(*) > 1;
GO

-- Identify invalid forecast values such as zero or negative units (Model sanity check)
SELECT * FROM dbo.Demand_Predictions
WHERE Predicted_Units <= 0;
GO

-- Check how recently the model was executed to ensure forecasts are fresh
SELECT MAX(Execution_Date) AS Last_Execution_Timestamp
FROM dbo.Demand_Predictions;
GO

-- Aggregate total forecasted volume by date to identify spikes
SELECT Date, SUM(Predicted_Units) AS Daily_Total_Forecast
FROM dbo.Demand_Predictions
GROUP BY Date
ORDER BY Date ASC;
GO

-- Compare prediction volume distribution across products
SELECT Product, AVG(Predicted_Units) AS Avg_Forecasted_Units, STDEV(Predicted_Units) AS Forecast_Volatility
FROM dbo.Demand_Predictions
GROUP BY Product;
GO

-- Retrieve the forecast horizon for each product
SELECT Product, MIN(Date) AS Horizon_Start, MAX(Date) AS Horizon_End
FROM dbo.Demand_Predictions
GROUP BY Product;
GO

-- Check for missing days in the prediction series (Potential gaps in forecasting)
SELECT Date, COUNT(Product) AS Product_Count
FROM dbo.Demand_Predictions
GROUP BY Date
HAVING COUNT(Product) < (SELECT COUNT(DISTINCT Product) FROM dbo.Demand_Predictions)
ORDER BY Date ASC;
GO

-- Join Actuals vs Predictions to calculate variance
SELECT 
    a.Date, 
    a.Product, 
    a.Units_Sold AS Actual_Value, 
    p.Predicted_Units AS Forecast_Value,
    (a.Units_Sold - p.Predicted_Units) AS Variance
FROM dbo.Demand_Forecast a
INNER JOIN dbo.Demand_Predictions p ON a.Date = p.Date AND a.Product = p.Product
ORDER BY a.Date DESC;
GO