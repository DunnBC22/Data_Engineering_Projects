-- database name: property_sales_db
-- owner: airflow

CREATE TABLE property_sales (
    PropType VARCHAR,
    Taxkey BIGINT,
    PropAddress VARCHAR,
    CondoProject VARCHAR,
    District INTEGER,
    Nbhd INTEGER,
    House_style VARCHAR,
    Extwall VARCHAR,
    Stories FLOAT,
    Year_Built INTEGER,
    Nr_of_rms INTEGER,
    Fin_sqft INTEGER,
    Units INTEGER,
    Bdrms INTEGER,
    Fbath INTEGER,
    Hbath INTEGER,
    Lotsize INTEGER,
    Sale_date VARCHAR,
    Sale_price INTEGER
);

COPY property_sales(
    PropType,
    Taxkey,
    PropAddress,
    CondoProject,
    District,
    Nbhd,
    House_style,
    Extwall,
    Stories,
    Year_Built,
    Nr_of_rms,
    Fin_sqft,
    Units,
    Bdrms,
    Fbath,
    Hbath,
    Lotsize,
	Sale_date,
    Sale_price
    )
FROM '/Users/briandunn/Desktop/Projects 2/Property Sales Data - Exploring Real Estate Trends/2002-2018-property-sales-data.csv'
DELIMITER ','
CSV HEADER;