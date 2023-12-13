-- database name: postcode_acc_risk_pred_db
-- owner: airflow

-- create a temp table to manipulate the date column format
CREATE TEMPORARY TABLE temp_table (
    Accident_ID INTEGER,
    Police_Force INTEGER,
    Number_of_Vehicles INTEGER,
    Number_of_Casualties INTEGER,
    Event_Date VARCHAR,
    Day_of_Week INTEGER,
    Event_Time TIME,
    Local_Authority_District INTEGER,
    Local_Authority_Highway VARCHAR,
    first_Road_Class INTEGER,
    first_Road_Number INTEGER,
    Road_Type VARCHAR,
    Speed_limit INTEGER,
    second_Road_Class INTEGER,
    second_Road_Number INTEGER,
    Pedestrian_Crossing_Human_Control VARCHAR,
    Pedestrian_Crossing_Physical_Facilities VARCHAR,
    Light_Conditions VARCHAR,
    Weather_Conditions VARCHAR,
    Road_Surface_Conditions VARCHAR,
    Special_Conditions_at_Site VARCHAR,
    Carriageway_Hazards VARCHAR,
    Urban_or_Rural_Area VARCHAR,
    Did_Police_Officer_Attend_Scene_of_Accident VARCHAR,
    State_Name VARCHAR,
    postcode VARCHAR,
    Country_Name VARCHAR
);

DROP TABLE IF EXISTS postcode_acc_risk_pred;

CREATE TABLE postcode_acc_risk_pred (
    Accident_ID INTEGER,
    Police_Force INTEGER,
    Number_of_Vehicles INTEGER,
    Number_of_Casualties INTEGER,
    Event_Date DATE,
    Day_of_Week INTEGER,
    Event_Time TIME,
    Local_Authority_District INTEGER,
    Local_Authority_Highway VARCHAR,
    first_Road_Class INTEGER,
    first_Road_Number INTEGER,
    Road_Type VARCHAR,
    Speed_limit INTEGER,
    second_Road_Class INTEGER,
    second_Road_Number INTEGER,
    Pedestrian_Crossing_Human_Control VARCHAR,
    Pedestrian_Crossing_Physical_Facilities VARCHAR,
    Light_Conditions VARCHAR,
    Weather_Conditions VARCHAR,
    Road_Surface_Conditions VARCHAR,
    Special_Conditions_at_Site VARCHAR,
    Carriageway_Hazards VARCHAR,
    Urban_or_Rural_Area VARCHAR,
    Did_Police_Officer_Attend_Scene_of_Accident VARCHAR,
    State_Name VARCHAR,
    postcode VARCHAR,
    Country_Name VARCHAR
);

COPY temp_table(
    Accident_ID,
    Police_Force,
    Number_of_Vehicles,
    Number_of_Casualties,
    Event_Date,
    Day_of_Week,
    Event_Time,
    Local_Authority_District,
    Local_Authority_Highway,
    first_Road_Class,
    first_Road_Number,
    Road_Type,
    Speed_limit,
    second_Road_Class,
    second_Road_Number,
    Pedestrian_Crossing_Human_Control,
    Pedestrian_Crossing_Physical_Facilities,
    Light_Conditions,
    Weather_Conditions,
    Road_Surface_Conditions,
    Special_Conditions_at_Site,
    Carriageway_Hazards,
    Urban_or_Rural_Area,
    Did_Police_Officer_Attend_Scene_of_Accident,
    State_Name,
    postcode,
    Country_Name
    )
FROM '/Users/briandunn/Desktop/Projects 2/Predict Accident Risk Score for Unique postcodes/train.csv'
DELIMITER ','
CSV HEADER;

-- reformat Event_Date column properly
UPDATE temp_table
SET Event_Date = TO_DATE(Event_Date, 'DD-MM-YYYY');

-- insert data with correct date format into main table
INSERT INTO postcode_acc_risk_pred (
    Accident_ID,
    Police_Force,
    Number_of_Vehicles,
    Number_of_Casualties,
    Event_Date,
    Day_of_Week,
    Event_Time,
    Local_Authority_District,
    Local_Authority_Highway,
    first_Road_Class,
    first_Road_Number,
    Road_Type,
    Speed_limit,
    second_Road_Class,
    second_Road_Number,
    Pedestrian_Crossing_Human_Control,
    Pedestrian_Crossing_Physical_Facilities,
    Light_Conditions,
    Weather_Conditions,
    Road_Surface_Conditions,
    Special_Conditions_at_Site,
    Carriageway_Hazards,
    Urban_or_Rural_Area,
    Did_Police_Officer_Attend_Scene_of_Accident,
    State_Name,
    postcode,
    Country_Name
    ) 
    SELECT 
        Accident_ID,
        Police_Force,
        Number_of_Vehicles,
        Number_of_Casualties,
        Event_Date::DATE,
        Day_of_Week,
        Event_Time,
        Local_Authority_District,
        Local_Authority_Highway,
        first_Road_Class,
        first_Road_Number,
        Road_Type,
        Speed_limit,
        second_Road_Class,
        second_Road_Number,
        Pedestrian_Crossing_Human_Control,
        Pedestrian_Crossing_Physical_Facilities,
        Light_Conditions,
        Weather_Conditions,
        Road_Surface_Conditions,
        Special_Conditions_at_Site,
        Carriageway_Hazards,
        Urban_or_Rural_Area,
        Did_Police_Officer_Attend_Scene_of_Accident,
        State_Name,
        postcode,
        Country_Name
    FROM temp_table;