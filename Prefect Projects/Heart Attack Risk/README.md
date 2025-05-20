# Heart Attack Risk - Prefect Pipeline

## Description

These are the transformations I applied to this dataset:

- Rename Features
    - "Age": "PatientAge",
    - "Gender": "PatientGender",
    - "Smoking": "SmokingStatus",
    - "Alcohol_Consumption": "AlcoholConsumption",
    - "Physical_Activity_Level": "PhysicalActivityLevel",
    - "BMI": "PatientBodyMassIndex",
    - "Cholesterol_Level": "CholesterolLevel",
    - "Resting_BP": "RestingBloodPressure",
    - "Heart_Rate": "HeartRate",
    - "Family_History": "FamilyHistory",
    - "Stress_Level": "StressLevel",
    - "Chest_Pain_Type": "ChestPainType",
    - "Fasting_Blood_Sugar": "FastingBloodSugar",
    - "ECG_Results": "EcgResults",
    - "Exercise_Induced_Angina": "ExerciseInducedAngina",
    - "Max_Heart_Rate_Achieved": "MaxHeartRateAchieved",
    - "Heart_Attack_Risk": "HeartAttackRisk"
- Clean Values
    - Remove leading and trailing whitespace:
        - PatientGender
        - PhysicalActivityLevel
        - StressLevel
        - ChestPainType
        - Thalassemia
        - EcgResults
        - HeartAttackRisk
    - Since the following features will be One Hot Encoded at some point, I am going to clean up the value in preparation for that:
        - EcgResults (Replace - dashes with space THEN titlecase THEN remove all whitespace)
        - Thalassemia (titlecase THEN remove all whitespace)
        - ChestPainType (Replace - dashes with space THEN titlecase THEN remove all whitespace)

- There are NO missing values.

## Dataset Source
https://www.kaggle.com/datasets/arifmia/heart-attack-risk-dataset