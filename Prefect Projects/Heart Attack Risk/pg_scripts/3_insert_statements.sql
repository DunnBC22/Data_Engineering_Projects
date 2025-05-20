\c ha_risk_pg_db;

COPY ha_risk_pg_table (
	"Age",
    "Gender",
    "Smoking",
    "Alcohol_Consumption",
    "Physical_Activity_Level",
    "BMI",
    "Diabetes",
    "Hypertension",
    "Cholesterol_Level",
    "Resting_BP",
    "Heart_Rate",
    "Family_History",
    "Stress_Level",
    "Chest_Pain_Type",
    "Thalassemia",
    "Fasting_Blood_Sugar",
    "ECG_Results",
    "Exercise_Induced_Angina",
    "Max_Heart_Rate_Achieved",
    "Heart_Attack_Risk"

)
FROM '/data/dataset.csv'
DELIMITER ','
CSV HEADER;