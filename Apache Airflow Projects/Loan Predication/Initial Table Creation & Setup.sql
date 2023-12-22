-- database name: loan_pred_db
-- owner: airflow

CREATE TABLE loan_pred (
    Loan_ID VARCHAR,
    Gender VARCHAR,
    Married VARCHAR,
    Dependents VARCHAR,
    Education VARCHAR,
    Self_Employed VARCHAR,
    ApplicantIncome INTEGER,
    CoapplicantIncome FLOAT,
    LoanAmount INTEGER,
    Loan_Amount_Term INTEGER,
    Credit_History INTEGER,
    Property_Area VARCHAR,
    Loan_Status VARCHAR
);

COPY loan_pred(
    Loan_ID,
    Gender,
    Married,
    Dependents,
    Education,
    Self_Employed,
    ApplicantIncome,
    CoapplicantIncome,
    LoanAmount,
    Loan_Amount_Term,
    Credit_History,
    Property_Area,
    Loan_Status
    )
FROM '/Users/briandunn/Desktop/Projects 2/Loan Predication/data.csv'
DELIMITER ','
CSV HEADER;