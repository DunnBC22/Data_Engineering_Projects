-- database name: house_price_pred_db
-- owner: airflow

CREATE TABLE house_price_pred (
    property_id INTEGER,
    location_id INTEGER,
    page_url VARCHAR,
    property_type VARCHAR,
    price INTEGER,
    Location_Code VARCHAR,
    City VARCHAR,
    Province_Name VARCHAR,
    Latitude FLOAT(4),
    Longitude FLOAT(4),
    Baths INTEGER,
    Area VARCHAR,
    Purpose VARCHAR,
    Bedrooms INTEGER,
    Date_Added DATE,
    Agency VARCHAR,
    Agent VARCHAR,
    Area_Type VARCHAR,
    Area_Size FLOAT(4),
    Area_Category VARCHAR
);

COPY house_price_pred(
    property_id,
    location_id,
    page_url,
    property_type,
    price,
    location_code,
    city,
    province_name,
    latitude,
    longitude,
    baths,
    area,
    purpose,
    bedrooms,
    date_added,
    agency,
    agent,
    Area_Type,
    Area_Size,
    Area_Category
    )
FROM '/Users/briandunn/Desktop/Projects 2/House Price Prediction (Zameen.com dataset)/zameen-updated.csv'
DELIMITER ','
CSV HEADER;