--database name: healthcare_insurance_db
-- owner: airflow;

DROP TABLE IF EXISTS healthcare_insurance;

CREATE TABLE healthcare_insurance (
    age INTEGER,
    sex VARCHAR,
    bmi FLOAT,
    children INTEGER,
    smoker VARCHAR,
    region VARCHAR,
    charges FLOAT
);

COPY healthcare_insurance(
    age,
    sex,
    bmi,
    children,
    smoker,
    region,
    charges
    )
FROM '/Users/briandunn/Desktop/Projects 2/Healthcare Insurance/insurance.csv'
DELIMITER ','
CSV HEADER;