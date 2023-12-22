-- database name: ee_dataset_db
-- owner: airflow

CREATE TABLE ee_dataset (
    Education VARCHAR,
    JoiningYear INTEGER,
    City VARCHAR,
    PaymentTier INTEGER,
    Age INTEGER,
    Gender VARCHAR,
    EverBenched VARCHAR,
    ExperienceInCurrentDomain INTEGER,
    LeaveOrNot INTEGER
);

COPY ee_dataset(
    Education,
    JoiningYear,
    City,
    PaymentTier,
    Age,
    Gender,
    EverBenched,
    ExperienceInCurrentDomain,
    LeaveOrNot
    )
FROM '/Users/briandunn/Desktop/Projects 2/Employee Dataset/Employee.csv'
DELIMITER ','
CSV HEADER;