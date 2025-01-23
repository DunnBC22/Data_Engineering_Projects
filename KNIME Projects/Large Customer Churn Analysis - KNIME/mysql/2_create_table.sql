USE lccd_mysql_db;

-- Create companies table
DROP TABLE IF EXISTS lccd_mysql_table;
CREATE TABLE lccd_mysql_table (
   CustomerID INTEGER,
    Gender VARCHAR(8),
    Age INTEGER,
    Geography VARCHAR(10),
    Tenure INTEGER,
    Contract VARCHAR(20),
    MonthlyCharges FLOAT,
    TotalCharges FLOAT,
    PaymentMethod VARCHAR(20),
    IsActiveMember INTEGER,
    Churn VARCHAR(6)
);

-- Grant SELECT permission to mysql
GRANT SELECT, UPDATE, INSERT ON lccd_mysql_table TO 'mysql'@'%';
FLUSH PRIVILEGES;