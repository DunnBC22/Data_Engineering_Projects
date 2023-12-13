-- database name: cust_shop_trends_db
-- owner: airflow

CREATE TABLE customer_shopping_trends (
    CustomerID INTEGER,
    Age INTEGER,
    Gender VARCHAR,
    ItemPurchased VARCHAR,
    Category VARCHAR,
    PurchaseAmount INTEGER,
    PurchaseLocation VARCHAR,
    ItemSize VARCHAR,
    Color VARCHAR,
    Season VARCHAR,
    ReviewRating FLOAT,
    SubscriptionStatus VARCHAR,
    ShippingType VARCHAR,
    DiscountApplied VARCHAR,
    PromoCodeUsed VARCHAR,
    PreviousPurchases INTEGER,
    PaymentMethod VARCHAR,
    FrequencyOfPurchases VARCHAR
);

COPY customer_shopping_trends(
    CustomerID,
    Age,
    Gender,
    ItemPurchased,
    Category,
    PurchaseAmount,
    PurchaseLocation,
    ItemSize,
    Color,
    Season,
    ReviewRating,
    SubscriptionStatus,
    ShippingType,
    DiscountApplied,
    PromoCodeUsed,
    PreviousPurchases,
    PaymentMethod,
    FrequencyOfPurchases
    )
FROM '/Users/briandunn/Desktop/Projects 2/Customer Shopping Trends/shopping_trends_updated.csv'
DELIMITER ','
CSV HEADER;