\c impact_analysis;

DROP TABLE IF EXISTS companies;
CREATE TABLE companies (company_id INTEGER PRIMARY KEY NOT NULL,company_name VARCHAR,company_location VARCHAR,company_type VARCHAR,employees VARCHAR);
GRANT SELECT ON companies TO pg;

DROP TABLE IF EXISTS economic_data;
CREATE TABLE economic_data (econ_data_id INTEGER PRIMARY KEY NOT NULL,econ_date VARCHAR,unemployment_rate FLOAT,gdp_value VARCHAR,cpi FLOAT,mortgage_rate_30y FLOAT);
GRANT SELECT ON economic_data TO pg;

DROP TABLE IF EXISTS purchases;
CREATE TABLE purchases (purchase_id INTEGER PRIMARY KEY NOT NULL,purchases_date TIMESTAMP,company_id INTEGER,product_category VARCHAR,quantity INTEGER,revenue FLOAT);
GRANT SELECT ON purchases TO pg;