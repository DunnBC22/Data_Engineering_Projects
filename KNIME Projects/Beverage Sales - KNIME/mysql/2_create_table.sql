USE beverage_sales_mysql_db;

-- Create companies table
DROP TABLE IF EXISTS beverage_sales_mysql_table;
CREATE TABLE beverage_sales_mysql_table (
    Order_ID VARCHAR(12),
    Customer_ID VARCHAR(12),
    Customer_Type VARCHAR(6),
    Product VARCHAR(25),
    Category VARCHAR(25),
    Unit_Price FLOAT,
    Quantity INTEGER,
    Discount FLOAT,
    Total_Price FLOAT,
    Region VARCHAR(28),
    Order_Date VARCHAR(15)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON beverage_sales_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;