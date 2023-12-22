-- database name: auto_insurance_db
-- owner: airflow

CREATE TABLE auto_insurance (
    Customer VARCHAR,
    Customer_State VARCHAR,
    Customer_Lifetime_Value FLOAT,
    Response VARCHAR,
    Coverage VARCHAR,
    Education VARCHAR,
    Effective_To_Date DATE,
    EmploymentStatus VARCHAR,
    Gender VARCHAR,
    Income INTEGER,
    Location_Code VARCHAR,
    Marital_Status VARCHAR,
    Monthly_Premium_Auto INTEGER,
    Months_Since_Last_Claim INTEGER,
    Months_Since_Policy_Inception INTEGER,
    Number_of_Open_Complaints INTEGER,
    Number_of_Policies INTEGER,
    Policy_Type VARCHAR,
    Policy_Name VARCHAR,
    Renew_Offer_Type VARCHAR,
    Sales_Channel VARCHAR,
    Total_Claim_Amount FLOAT,
    Vehicle_Class VARCHAR,
    Vehicle_Size VARCHAR
);

COPY auto_insurance(
    Customer,
    Customer_State,
    Customer_Lifetime_Value,
    Response,
    Coverage,
    Education,
    Effective_To_Date,
    EmploymentStatus,
    Gender,
    Income,
    Location_Code,
    Marital_Status,
    Monthly_Premium_Auto,
    Months_Since_Last_Claim,
    Months_Since_Policy_Inception,
    Number_of_Open_Complaints,
    Number_of_Policies,
    Policy_Type,
    Policy_Name,
    Renew_Offer_Type,
    Sales_Channel,
    Total_Claim_Amount,
    Vehicle_Class,
    Vehicle_Size
    )
FROM '/Users/briandunn/Desktop/Projects 2/Insurance/AutoInsurance.csv'
DELIMITER ','
CSV HEADER;