CREATE TABLE AVERAGE_HOURLY_FITBIT_DATA AS 
    SELECT 
        hc.activity_hour AS Activity_Hour,
        AVG(hc.calories) AS Average_Hourly_Calories,
        AVG(hs.step_total) AS Average_Hourly_Steps
    FROM 
        hourly_calories hc
    INNER JOIN
        hourly_steps hs 
    WITHIN 10 HOURS
    GRACE PERIOD 2 HOURS
    ON 
        hc.id = hs.id
    GROUP BY
        hc.activity_hour
    EMIT CHANGES;