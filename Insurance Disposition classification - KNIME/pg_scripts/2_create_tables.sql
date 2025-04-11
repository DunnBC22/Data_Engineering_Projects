\c insurance_dispostion_clf_pg_db;

CREATE TABLE IF NOT EXISTS insur_claim_info_pg_table (
    "Claim Number" VARCHAR(15),
    "City Code" VARCHAR(6),
    "City" VARCHAR(18),
    "Enterprise Type" VARCHAR(45),
    "Claim Type" VARCHAR(25),
    "Claim Site" VARCHAR(15),
    "Product Insured" VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS insur_date_data_pg_table (
    "Claim Number" VARCHAR(15),
    "Incident Date" VARCHAR(15),
    "Date Received" VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS insur_result_data_pg_table (
    "Claim Number" VARCHAR(15),
    "Claim Amount" FLOAT,
    "Close Amount" FLOAT,
    "Disposition" VARCHAR(20)
);