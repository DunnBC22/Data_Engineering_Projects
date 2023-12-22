-- database name: covid19_pred_db
-- owner: airflow

DROP TABLE IF EXISTS temp_table;

-- create a temp table to manipulate the date column format
CREATE TEMPORARY TABLE temp_table (
    Ind_ID INTEGER,
    Test_date TEXT,
    Cough_symptoms VARCHAR,
    Fever VARCHAR,
    Sore_throat VARCHAR,
    Shortness_of_breath VARCHAR,
    Headache VARCHAR,
    Corona VARCHAR,
    Age_60_above VARCHAR,
    Sex VARCHAR,
    Known_contact VARCHAR
);

CREATE TABLE IF NOT EXISTS covid19_pred (
    Ind_ID INTEGER,
    Test_date DATE,
    Cough_symptoms VARCHAR,
    Fever VARCHAR,
    Sore_throat VARCHAR,
    Shortness_of_breath VARCHAR,
    Headache VARCHAR,
    Corona VARCHAR,
    Age_60_above VARCHAR,
    Sex VARCHAR,
    Known_contact VARCHAR
);

COPY temp_table(
    Ind_ID, 
    Test_date,
    Cough_symptoms, 
    Fever, 
    Sore_throat, 
    Shortness_of_breath, 
    Headache, 
    Corona, 
    Age_60_above, 
    Sex, 
    Known_contact
    )
FROM '/Users/briandunn/Desktop/Projects 2/COVID19 Project/corona.csv'
DELIMITER ','
CSV HEADER;

-- reformat the Test_date column properly
UPDATE temp_table
SET Test_date = TO_DATE(Test_date, 'DD-MM-YYYY');

-- Insert the cleaned data into the covid19_pred table
INSERT INTO covid19_pred(
    Ind_ID, 
    Test_date,
    Cough_symptoms, 
    Fever, 
    Sore_throat, 
    Shortness_of_breath, 
    Headache, 
    Corona, 
    Age_60_above, 
    Sex, 
    Known_contact
    )
	SELECT 
    Ind_ID, 
    Test_date::DATE,
    Cough_symptoms, 
    Fever, 
    Sore_throat, 
    Shortness_of_breath, 
    Headache, 
    Corona, 
    Age_60_above, 
    Sex, 
    Known_contact
	FROM temp_table;

GRANT SELECT, INSERT, UPDATE, DELETE ON covid19_pred TO airflow;

-- other commands used to make it work

DROP TABLE IF EXISTS covid_19_prediction_clf_pipeline;
CREATE TABLE covid_19_prediction_clf_pipeline(
	id_placeholder INTEGER,
	something_text TEXT
);

GRANT SELECT, INSERT, UPDATE, DELETE ON covid_19_prediction_clf_pipeline TO airflow;