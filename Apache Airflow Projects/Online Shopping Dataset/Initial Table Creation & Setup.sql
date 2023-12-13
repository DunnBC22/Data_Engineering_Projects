-- database name: online_shopping_db
-- owner: airflow;

CREATE TABLE online_shopping (
    record_id INTEGER,
    CustomerID FLOAT,
    Gender VARCHAR,
    Customer_Location VARCHAR,
    Tenure_Months FLOAT,
    Transaction_ID FLOAT,
    Transaction_Date TIMESTAMP,
    Product_SKU VARCHAR,
    Product_Description VARCHAR,
    Product_Category VARCHAR,
    Quantity FLOAT,
    Avg_Price FLOAT,
    Delivery_Charges FLOAT,
    Coupon_Status VARCHAR,
    GST	FLOAT,
    Transaction_Date_2 TIMESTAMP,
    Offline_Spend FLOAT,
    Online_Spend FLOAT,
    Transaction_Month INTEGER,
    Coupon_Code VARCHAR,
    Discount_pct FLOAT
);

COPY online_shopping(
	record_id,
	CustomerID,
    Gender,
    Customer_Location,
    Tenure_Months,
    Transaction_ID,
    Transaction_Date,
    Product_SKU,
    Product_Description,
    Product_Category,
    Quantity,
    Avg_Price,
    Delivery_Charges,
    Coupon_Status,
    GST,
    Transaction_Date_2,
    Offline_Spend,
    Online_Spend,
    Transaction_Month,
    Coupon_Code,
    Discount_pct
    )
FROM '/Users/briandunn/Desktop/Projects 2/Online Shopping Dataset/file.csv'
DELIMITER ','
CSV HEADER;