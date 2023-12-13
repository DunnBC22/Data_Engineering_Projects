-- db name: travel_insurance_db
-- owner: airflow;

CREATE TABLE IF NOT EXISTS travel_insurance (
    Agency VARCHAR,
    Agency_Type VARCHAR,
    Distribution_Channel VARCHAR,
    Product_Name VARCHAR,
    Claim VARCHAR,
    Duration INTEGER,
    Destination VARCHAR,
    Net_Sales FLOAT,
    Commission FLOAT,
    Gender VARCHAR,
    Age INTEGER
);

COPY travel_insurance(
    Agency,
    Agency_Type,
    Distribution_Channel,
    Product_Name,
    Claim,
    Duration,
    Destination,
    Net_Sales,
    Commission,
    Gender,
    Age
    )
FROM '/Users/briandunn/Desktop/Projects 2//.csv'
DELIMITER ','
CSV HEADER;