CREATE TABLE minutes_fitbit_data AS 
    SELECT 
        ms.id AS ID,
        SUM(ms.date_and_time) AS Date_And_Time,
        SUM(ms.sleep_minutes) AS Sleep_Minutes,
        SUM(ms.log_id) AS Log_ID,
        SUM(msn.mets) AS METs,
        AVG(mina.intensity) AS Average_Intensity,
        SUM(mcn.calories) AS Total_Calories
    FROM 
        minute_sleep ms
    INNER JOIN 
        minute_steps_narrow msn 
    WINDOW 
        10 YEARS
    GRACE PERIOD 
        2 YEARS
    ON 
        ms.id=msn.id
    INNER JOIN 
        minute_intensities_narrow mina 
    WINDOW 
        10 YEARS
    GRACE PERIOD 
        2 YEARS
    ON 
        ms.id=mina.id
    INNER JOIN 
        minute_calories_narrow mcn 
    WINDOW 
        10 YEARS
    GRACE PERIOD 
        2 YEARS
    ON 
        ms.id=mcn.id
    EMIT CHANGES;