\c mock_marketing_data;

DROP TABLE IF EXISTS account;
CREATE TABLE account (id INTEGER PRIMARY KEY NOT NULL,cust_id VARCHAR,acquisition_cost FLOAT,internet_banking_indicator VARCHAR,date_first_account_opened VARCHAR,date_last_account_opened VARCHAR,pursuit VARCHAR,primary_advisor_organization_id INTEGER,primary_branch_proximity INTEGER,primary_spoken_language VARCHAR,primary_written_language VARCHAR,satisfaction_rating_from_survey VARCHAR,secondary_advisor_id INTEGER,secondary_advisor_organization_id INTEGER,special_te VARCHAR);
GRANT SELECT ON account TO pg;


DROP TABLE IF EXISTS customer;
CREATE TABLE customer (id INTEGER PRIMARY KEY NOT NULL,cust_id VARCHAR,gender VARCHAR,first_name VARCHAR,last_name VARCHAR,email VARCHAR,ssn VARCHAR,age_range VARCHAR, annual_income VARCHAR,birth_year INTEGER,current_employment_start_date VARCHAR,customer_behavior VARCHAR,education_level VARCHAR,employment_status VARCHAR,marital_status VARCHAR,monthly_net_income INTEGER,profession VARCHAR,retirement_age INTEGER,customer_status VARCHAR,wallet_share_percentage INTEGER);
GRANT SELECT ON customer TO pg;


DROP TABLE IF EXISTS financials;
CREATE TABLE financials (id INTEGER PRIMARY KEY NOT NULL,cust_id VARCHAR,monthly_housing_cost INTEGER,contact_preference VARCHAR,credit_authority_level VARCHAR,credit_score INTEGER,credit_utilization FLOAT,debt_service_coverage_ratio INTEGER);
GRANT SELECT ON financials TO pg;


DROP TABLE IF EXISTS household;
CREATE TABLE household (id INTEGER PRIMARY KEY NOT NULL,cust_id VARCHAR,household_id VARCHAR,household_address VARCHAR,household_city VARCHAR,household_country VARCHAR,household_state VARCHAR,household_zip_code VARCHAR,address_last_changed_date VARCHAR,number_of_dependent_adults INTEGER,number_of_dependent_children INTEGER,family_size INTEGER,head_of_household_indicator VARCHAR,home_owner_indicator VARCHAR,urban_code VARCHAR,primary_advisor_id INTEGER);
GRANT SELECT ON household TO pg;


DROP TABLE IF EXISTS marketing;
CREATE TABLE marketing (id INTEGER PRIMARY KEY NOT NULL,cust_id VARCHAR,advertising_indicator VARCHAR,attachment_allowed_indicator VARCHAR,preferred_communication_form VARCHAR,importance_level_code VARCHAR,influence_score BIGINT,market_group VARCHAR,loyalty_rating_code BIGINT,recorded_voice_sample_id BIGINT,referrals_value_code VARCHAR,relationship_start_date VARCHAR);
GRANT SELECT ON marketing TO pg;
