GRANT SELECT ON ha_risk_mysql_db.* TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- drop table, if exists, to start from scratch
DROP TABLE IF EXISTS ha_risk_mysql_table;

-- Create ha_risk_mysql_table Table
CREATE TABLE ha_risk_mysql_table (
    Id INT,
    PatientAge INTEGER,
    PatientGender VARCHAR(10),
    SmokingStatus INTEGER,
    AlcoholConsumption INTEGER,
    PhysicalActivityLevel VARCHAR(12),
    PatientBodyMassIndex FLOAT,
    Diabetes INTEGER,
    Hypertension INTEGER,
    CholesterolLevel FLOAT,
    RestingBloodPressure INTEGER,
    HeartRate INTEGER,
    FamilyHistory INTEGER,
    StressLevel VARCHAR(12),
    ChestPainType VARCHAR(18),
    Thalassemia VARCHAR(21),
    FastingBloodSugar INTEGER,
    EcgResults VARCHAR(35),
    ExerciseInducedAngina INTEGER,
    MaxHeartRateAchieved INTEGER,
    HeartAttackRisk VARCHAR(12)
);