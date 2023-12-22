-- database name: gourmet_food_procurement_db
-- owner: airflow

CREATE TABLE gourmet_food_procurement (
    Agency VARCHAR,
    TimePeriod VARCHAR,
    Food_Product_Group VARCHAR,
    Food_Product_Category VARCHAR,
    Product_Name VARCHAR,
    Product_Type VARCHAR,
    OriginDetail VARCHAR,
    Distributor VARCHAR,
    Vendor VARCHAR,
    Num_Of_Units INTEGER,
    Total_Weight_in_lbs INTEGER,
    Total_Cost INTEGER
);

COPY gourmet_food_procurement(
    Agency,
    TimePeriod,
    Food_Product_Group,
    Food_Product_Category,
    Product_Name,
    Product_Type,
    OriginDetail,
    Distributor,
	Vendor,
    Num_Of_Units,
    Total_Weight_in_lbs,
    Total_Cost
    )
FROM '/Users/briandunn/Desktop/Projects 2/Gourmet Food Procurement Data/Good_Food_Purchasing_Data.csv'
DELIMITER ','
CSV HEADER;