\c ha_risk_pg_db;

CREATE TABLE IF NOT EXISTS ha_risk_pg_table (
    Age INTEGER,
    Gender VARCHAR(9),
    Smoking INTEGER,
    Alcohol_Consumption INTEGER,
    Physical_Activity_Level VARCHAR(12),
    BMI FLOAT,
    Diabetes INTEGER,
    Hypertension INTEGER,
    Cholesterol_Level FLOAT,
    Resting_BP INTEGER,
    Heart_Rate INTEGER,
    Family_History INTEGER,
    Stress_Level VARCHAR(12),
    Chest_Pain_Type VARCHAR(20),
    Thalassemia VARCHAR(25),
    Fasting_Blood_Sugar INTEGER,
    ECG_Results VARCHAR(36),
    Exercise_Induced_Angina INTEGER,
    Max_Heart_Rate_Achieved INTEGER,
    Heart_Attack_Risk VARCHAR(12)
);