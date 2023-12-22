-- database name: hosp_insur_claim_fraud_db
-- owner: airflow;

CREATE TABLE hosp_insur_claim_fraud (
    area_Service VARCHAR,
    hospital_County VARCHAR,
    hospital_Id INTEGER,
    age VARCHAR,
    gender VARCHAR,
    cultural_group VARCHAR,
    ethnicity VARCHAR,
    days_spend_hsptl VARCHAR,
    admission_type VARCHAR,
    home_or_self_care VARCHAR,
    ccs_diagnosis_code INTEGER,
    ccs_procedure_code INTEGER,
    apr_drg_description VARCHAR,
    code_illness INTEGER,
    mortality_risk INTEGER,
    surg_Description VARCHAR,
    weight_baby INTEGER,
    abortion VARCHAR,
    emergency_dept_yes_No VARCHAR,
    tot_charg FLOAT,
    tot_cost FLOAT,
    ratio_of_total_costs_to_total_charges FLOAT,
    results INTEGER,
    payment_Typology INTEGER
);

COPY hosp_insur_claim_fraud(
    Area_Service,
    Hospital_County,
    hospital_Id,
    age,
    gender,
    cultural_group,
    ethnicity,
    days_spend_hsptl,
    admission_type,
    home_or_self_care,
    ccs_diagnosis_code,
    ccs_procedure_code,
    apr_drg_description,
    code_illness,
    mortality_risk,
    surg_Description,
    weight_baby,
    abortion,
    emergency_dept_yes_No,
    tot_charg,
    tot_cost,
    ratio_of_total_costs_to_total_charges,
    results,
    payment_Typology
    )
FROM '/Users/briandunn/Desktop/Projects 2/Hospital Insurance Claim Fraud/Insurance Dataset.csv'
DELIMITER ','
CSV HEADER;