-- database name: consumer_behavior_db
-- owner: airflow

CREATE TABLE consumer_behavior (
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

COPY consumer_behavior(
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
FROM '/Users/briandunn/Desktop/Projects 2/Consumer Behavior and Shopping Habits Dataset/shopping_behavior_updated.csv'
DELIMITER ','
CSV HEADER;