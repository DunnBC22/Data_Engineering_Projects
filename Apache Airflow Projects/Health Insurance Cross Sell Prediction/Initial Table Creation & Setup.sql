-- database name: hi_cross_sell_db
-- owner: airflow

CREATE TABLE hi_cross_sell (
    id INTEGER,
    Gender VARCHAR,
    Customer_Age INTEGER,
    Driving_License VARCHAR,
    Region_Code FLOAT,
    Previously_Insured INTEGER,
    Vehicle_Age VARCHAR,
    Vehicle_Damage VARCHAR,
    Annual_Premium FLOAT,
    Policy_Sales_Channel FLOAT,
    Vintage INTEGER,
    Response INTEGER
);

COPY hi_cross_sell(
    id,
    Gender,
    Customer_Age,
    Driving_License,
    Region_Code,
    Previously_Insured,
    Vehicle_Age,
    Vehicle_Damage,
    Annual_Premium,
    Policy_Sales_Channel,
    Vintage,
    Response
    )
FROM '/Users/briandunn/Desktop/Projects 2/Health Insurance Cross Sell Prediction/train.csv'
DELIMITER ','
CSV HEADER;