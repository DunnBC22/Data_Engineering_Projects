\c lccd_pg_db;

GRANT ALL PRIVILEGES ON DATABASE lccd_pg_db TO pg;

CREATE TABLE IF NOT EXISTS lccd_pg_table (
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