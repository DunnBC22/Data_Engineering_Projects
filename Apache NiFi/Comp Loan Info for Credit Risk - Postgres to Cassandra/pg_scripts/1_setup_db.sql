\c comp_loan_info_credit_risk_db_pg;

-- drop table, if exists, to start from scratch
DROP TABLE IF EXISTS comp_loan_info_credit_risk_table_pg;

-- create table
CREATE TABLE comp_loan_info_credit_risk_table_pg (
    id INTEGER,
    address_state VARCHAR,
    application_type VARCHAR,
    emp_length VARCHAR,
    emp_title VARCHAR,
    grade VARCHAR,
    home_ownership VARCHAR,
    issue_date VARCHAR,
    last_credit_pull_date VARCHAR,
    last_payment_date VARCHAR,
    loan_status VARCHAR,
    next_payment_date VARCHAR,
    member_id INTEGER,
    purpose VARCHAR,
    sub_grade VARCHAR,
    term VARCHAR,
    verification_status VARCHAR,
    annual_income FLOAT,
    dti FLOAT,
    installment FLOAT,
    int_rate FLOAT,
    loan_amount INTEGER,
    total_acc INTEGER,
    total_payment INTEGER
);

COPY comp_loan_info_credit_risk_table_pg
FROM '/docker-entrypoint-initdb.d/data.csv'
DELIMITER ','
CSV HEADER;


UPDATE comp_loan_info_credit_risk_table_pg
SET emp_title = COALESCE(emp_title, 'NULL');