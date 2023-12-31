-- database name: ins_claims_ds
--owner: airflow

CREATE TABLE insur_claims (
    months_as_customer INTEGER,
    customer_age INTEGER,
    policy_number INTEGER,
    policy_bind_date DATE,
    policy_state VARCHAR,
    policy_csl VARCHAR,
    policy_deductable INTEGER,
    policy_annual_premium FLOAT,
    umbrella_limit INTEGER,
    insured_zip INTEGER,
    insured_sex VARCHAR,
    insured_education_level VARCHAR,
    insured_occupation VARCHAR,
    insured_hobbies VARCHAR,
    insured_relationship VARCHAR,
    capital_gains INTEGER,
    capital_loss INTEGER,
    incident_date DATE,
    incident_type VARCHAR,
    collision_type VARCHAR,
    incident_severity VARCHAR,
    authorities_contacted VARCHAR,
    incident_state VARCHAR,
    incident_city VARCHAR,
    incident_location VARCHAR,
    incident_hour_of_the_day INTEGER,
    number_of_vehicles_involved INTEGER,
    property_damage VARCHAR,
    bodily_injuries INTEGER,
    witnesses INTEGER,
    police_report_available VARCHAR,
    total_claim_amount INTEGER,
    injury_claim INTEGER,
    property_claim INTEGER,
    vehicle_claim INTEGER,
    auto_make VARCHAR,
    auto_model VARCHAR,
    auto_year INTEGER,
    fraud_reported VARCHAR
);

COPY insur_claims(
    months_as_customer,
    customer_age,
    policy_number,
    policy_bind_date,
    policy_state,
    policy_csl,
    policy_deductable,
    policy_annual_premium,
    umbrella_limit,
    insured_zip,
    insured_sex,
    insured_education_level,
    insured_occupation,
    insured_hobbies,
    insured_relationship,
    capital_gains,
    capital_loss,
    incident_date,
    incident_type,
    collision_type,
    incident_severity,
    authorities_contacted,
    incident_state,
    incident_city,
    incident_location,
    incident_hour_of_the_day,
    number_of_vehicles_involved,
    property_damage,
    bodily_injuries,
    witnesses,
    police_report_available,
    total_claim_amount,
    injury_claim,
    property_claim,
    vehicle_claim,
    auto_make,
    auto_model,
    auto_year,
    fraud_reported
    )
FROM '/Users/briandunn/Desktop/Projects 2/Automobile Insurance/insurance_claims.csv'
DELIMITER ','
CSV HEADER;