-- database name: bank_cc_complaints
-- owner: airflow

CREATE TABLE complaints (
    date_received DATE,
    product VARCHAR,
    sub_product VARCHAR,
    issue VARCHAR,
    sub_issue VARCHAR,
    consumer_complaint_narrative VARCHAR,
    company_public_response VARCHAR,
    company VARCHAR,
    bank_state VARCHAR,
    zip_code VARCHAR,
    tags VARCHAR,
    consumer_consent_provided VARCHAR,
    submitted_via VARCHAR,
    date_sent_to_company DATE,
    company_response_to_consumer VARCHAR,
    timely_response VARCHAR,
    consumer_disputed VARCHAR,
    complaint_id INTEGER
);

COPY complaints(
    date_received,
    product,
    sub_product,
    issue,
    sub_issue,
    consumer_complaint_narrative,
    company_public_response,
    company,
    bank_state,
    zip_code,
    tags,
    consumer_consent_provided,
    submitted_via,
    date_sent_to_company,
    company_response_to_consumer,
    timely_response,
    consumer_disputed,
    complaint_id
    )
FROM '/Users/briandunn/Desktop/Projects 2/bank and cc complaints/data/bank_account_or_service_complaints.csv'
DELIMITER ','
CSV HEADER;

COPY complaints(
    date_received,
    product,
    sub_product,
    issue,
    sub_issue,
    consumer_complaint_narrative,
    company_public_response,
    company,
    bank_state,
    zip_code,
    tags,
    consumer_consent_provided,
    submitted_via,
    date_sent_to_company,
    company_response_to_consumer,
    timely_response,
    consumer_disputed,
    complaint_id
    )
FROM '/Users/briandunn/Desktop/Projects 2/bank and cc complaints/data/credit_card_complaints.csv'
DELIMITER ','
CSV HEADER;