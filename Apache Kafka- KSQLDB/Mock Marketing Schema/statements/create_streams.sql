-- Create stream: account
CREATE STREAM account (
    cust_id VARCHAR KEY,
    acquisition_cost DOUBLE,
    internet_banking_indicator VARCHAR,
    date_first_account_opened DATE,
    date_last_account_opened DATE,
    pursuit VARCHAR,
    primary_advisor_organization_id INTEGER,
    primary_branch_proximity INTEGER,
    primary_spoken_language VARCHAR,
    primary_written_language VARCHAR,
    satisfaction_rating_from_survey VARCHAR,
    secondary_advisor_id INTEGER,
    secondary_advisor_organization_id INTEGER,
    special_te VARCHAR
    )
    WITH (
        kafka_topic='account',
        value_format='json', 
        partitions=1
    );

-- Create stream: customer
CREATE STREAM customer (
    cust_id VARCHAR,
    gender VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    ssn VARCHAR,
    age_range VARCHAR, 
    annual_income VARCHAR,
    birth_year INTEGER,
    current_employment_start_date VARCHAR,
    customer_behavior VARCHAR,
    education_level VARCHAR,
    employment_status VARCHAR,
    marital_status VARCHAR,
    monthly_net_income INTEGER,
    profession VARCHAR,
    retirement_age INTEGER,
    customer_status VARCHAR,
    wallet_share_percentage INTEGER
    )
    WITH (
        kafka_topic='customer',
        value_format='json', 
        partitions=1
    );

-- Create stream: financials
CREATE STREAM financials (
    cust_id VARCHAR,
    monthly_housing_cost INTEGER,
    contact_preference VARCHAR,
    credit_authority_level VARCHAR,
    credit_score INTEGER,
    credit_utilization DOUBLE,
    debt_service_coverage_ratio INTEGER
    )
    WITH (
        kafka_topic='financials',
        value_format='json', 
        partitions=1
    );

-- Create stream: household
CREATE STREAM household (
    cust_id VARCHAR KEY,
    household_id VARCHAR,
    household_address VARCHAR,
    household_city VARCHAR,
    household_country VARCHAR,
    household_state VARCHAR,
    household_zip_code VARCHAR,
    address_last_changed_date VARCHAR,
    number_of_dependent_adults INTEGER,
    number_of_dependent_children INTEGER,
    family_size INTEGER,
    head_of_household_indicator VARCHAR,
    home_owner_indicator VARCHAR,
    urban_code VARCHAR,
    primary_advisor_id INTEGER
    )
    WITH (
        kafka_topic='household',
        value_format='json', 
        partitions=1
    );

-- Create stream: marketing
CREATE STREAM marketing (
    cust_id VARCHAR KEY,
    advertising_indicator VARCHAR,
    attachment_allowed_indicator VARCHAR,
    preferred_communication_form VARCHAR,
    importance_level_code VARCHAR,
    influence_score BIGINT,
    market_group VARCHAR,
    loyalty_rating_code BIGINT,
    recorded_voice_sample_id BIGINT,
    referrals_value_code VARCHAR,
    relationship_start_date VARCHAR
    )
    WITH (
        kafka_topic='marketing',
        value_format='json', 
        partitions=1
    );
