COPY insur_claim_info_pg_table (
	"Claim Number",
    "City Code",
    "City",
    "Enterprise Type",
    "Claim Type",
    "Claim Site",
    "Product Insured"
)
FROM '/data/Insurance_Claim_Info_data.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE insur_claim_info_pg_table
ADD COLUMN id INTEGER GENERATED ALWAYS AS IDENTITY;


COPY insur_date_data_pg_table (
	"Claim Number",
    "Incident Date",
    "Date Received"
)
FROM '/data/Insurance_Date_data.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE insur_date_data_pg_table
ADD COLUMN id INTEGER GENERATED ALWAYS AS IDENTITY;


COPY insur_result_data_pg_table (
	"Claim Number",
    "Claim Amount",
    "Close Amount",
    "Disposition"
)
FROM '/data/Insurance_Result_data.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE insur_result_data_pg_table
ADD COLUMN id INTEGER GENERATED ALWAYS AS IDENTITY;