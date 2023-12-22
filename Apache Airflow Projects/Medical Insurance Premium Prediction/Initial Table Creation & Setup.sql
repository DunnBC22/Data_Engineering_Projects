-- database name: med_ins_prem_pred_db
-- owner: airflow;

CREATE TABLE med_ins_prem_pred (
    Age INTEGER,
    Diabetes INTEGER,
    BloodPressureProblems INTEGER,
    AnyTransplants INTEGER,
    AnyChronicDiseases INTEGER,
    PatientHeight INTEGER,
    PatientWeight INTEGER,
    KnownAllergies INTEGER,
    HistoryOfCancerInFamily INTEGER,
    NumberOfMajorSurgeries INTEGER,
    PremiumPrice INTEGER
);

COPY med_ins_prem_pred(
    Age,
    Diabetes,
    BloodPressureProblems,
    AnyTransplants,
    AnyChronicDiseases,
    PatientHeight,
    PatientWeight,
    KnownAllergies,
    HistoryOfCancerInFamily,
    NumberOfMajorSurgeries,
    PremiumPrice
    )
FROM '/Users/briandunn/Desktop/Projects 2/Medical Insurance Premium Prediction/Medicalpremium.csv'
DELIMITER ','
CSV HEADER;