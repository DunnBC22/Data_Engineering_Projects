USE impact_analysis;

-- Create companies table
DROP TABLE IF EXISTS companies;
CREATE TABLE companies (
    company_id INT PRIMARY KEY NOT NULL,
    company_name VARCHAR(36),
    company_location VARCHAR(22),
    company_type VARCHAR(12),
    employees VARCHAR(15)
);
-- Grant SELECT permission to mysql
GRANT SELECT ON companies TO 'mysql'@'%';

-- Create economic_data table
DROP TABLE IF EXISTS economic_data;
CREATE TABLE economic_data (
    econ_data_id INT PRIMARY KEY NOT NULL,
    econ_date VARCHAR(36),
    unemployment_rate FLOAT,
    gdp_value VARCHAR(20),
    cpi FLOAT,
    mortgage_rate_30y FLOAT
);
-- Grant SELECT permission to mysql
GRANT SELECT ON economic_data TO 'mysql'@'%';

-- Create purchases table
DROP TABLE IF EXISTS purchases;
CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY NOT NULL,
    purchases_date TIMESTAMP,
    company_id INT,
    product_category VARCHAR(80),
    quantity INT,
    revenue FLOAT
);
-- Grant SELECT permission to mysql
GRANT SELECT ON purchases TO 'mysql'@'%';
