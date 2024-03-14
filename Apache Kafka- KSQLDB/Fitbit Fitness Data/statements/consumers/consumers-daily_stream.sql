CREATE STREAM DAILY_STREAM_FITBIT_DATA AS 
    SELECT 
        da.id AS ID,
        da.activity_date AS Activity_Date,
        da.total_distance AS Total_Distance,
        da.tracker_distance AS Tracker_Distance,
        da.logged_activities_distance AS Logged_Activities_Distance,
        da.very_active_distance AS Very_Active_Distance,
        da.moderately_active_distance AS Moderately_Active_Distance,
        da.light_active_distance AS Light_Active_Distance,
        da.sedentary_active_distance AS Sedentary_Active_Distance,
        da.very_active_minutes AS Very_Active_Minutes,
        da.fairly_active_minutes AS Fairly_Active_Minutes,
        da.lightly_active_minutes AS Lightly_Active_Minutes,
        da.sedentary_minutes AS Sedentary_Minutes,
        da.calories AS Calories,
        sd.total_sleep_records AS Total_Sleep_Records,
        sd.total_minutes_asleep AS Total_Time_Asleep_In_Minutes,
        sd.total_time_in_bed AS Total_Time_In_Bed,
        ds.step_total AS Step_Total
    FROM 
        daily_activity da
    LEFT JOIN
        daily_steps ds 
    WITHIN
        10 HOURS
    GRACE PERIOD 
        2 HOURS
    ON 
        da.id=ds.id
    LEFT JOIN
        sleep_day sd 
    WITHIN
        10 HOURS
    GRACE PERIOD 
        2 HOURS
    ON
        da.id=sd.id
    EMIT CHANGES;


/*
Error Message for the above shown statement:

Could not determine output schema for query due to error: Stream-Stream joins must have a WITHIN clause specified. None was provided. To learn about how to specify a WITHIN clause with a stream-stream join, please visit: https://docs.confluent.io/current/ksql/docs/syntax-reference.html#create-stream-as-select
*/