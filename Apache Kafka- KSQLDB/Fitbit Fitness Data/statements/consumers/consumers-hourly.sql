CREATE STREAM STREAM_HOURLY_FITBIT_DATA AS 
    SELECT 
        hi.id AS ID,
        hi.average_intensity AS Hourly_Average_intensity,
        hc.calories AS Hourly_Calories,
        hs.step_total AS Hourly_Step_Totals
    FROM 
        hourly_intensities hi
    INNER JOIN 
        hourly_calories hc 
    WITHIN 10 HOURS
    GRACE PERIOD 2 HOURS
    ON 
        hi.id = hc.id
    INNER JOIN 
        hourly_steps hs 
    WITHIN 10 HOURS
    GRACE PERIOD 2 HOURS
    ON 
        hi.id = hs.id
    EMIT CHANGES;