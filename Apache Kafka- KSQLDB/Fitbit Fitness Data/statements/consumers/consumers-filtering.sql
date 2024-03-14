CREATE TABLE DAILY_FILTERED_FITBIT_DATA AS 
    SELECT 
        da.activity_date AS Activity_Date,
        SUM(da.total_distance) AS Total_Distance,
        SUM(da.tracker_distance) AS Tracker_Distance,
        SUM(da.logged_activities_distance) AS Logged_Activities_Distance,
        SUM(da.very_active_distance) AS Very_Active_Distance,
        SUM(da.moderately_active_distance) AS Moderately_Active_Distance,
        SUM(da.light_active_distance) AS Light_Active_Distance,
        SUM(da.sedentary_active_distance) AS Sedentary_Active_Distance,
        SUM(da.very_active_minutes) AS Very_Active_Minutes,
        SUM(da.fairly_active_minutes) AS Fairly_Active_Minutes,
        SUM(da.lightly_active_minutes) AS Lightly_Active_Minutes,
        SUM(da.sedentary_minutes) AS Sedentary_Minutes,
        SUM(da.calories) AS Calories,
        SUM(sd.total_sleep_records) AS Total_Sleep_Records,
        SUM(sd.total_minutes_asleep) AS Total_Time_Asleep_In_Minutes,
        SUM(sd.total_time_in_bed) AS Total_Time_In_Bed,
        SUM(ds.step_total) AS Step_Total
    FROM 
        daily_activity da
    INNER JOIN
        daily_steps ds 
    WITHIN
        10 HOURS
    GRACE PERIOD 
        2 HOURS
    ON 
        da.id=ds.id
    INNER JOIN
        sleep_day sd 
    WITHIN
        10 HOURS
    GRACE PERIOD 
        2 HOURS
    ON
        da.id=sd.id
    WHERE 
        Tracker_Distance > Total_Distance
    GROUP BY
        da.activity_date
    EMIT CHANGES;