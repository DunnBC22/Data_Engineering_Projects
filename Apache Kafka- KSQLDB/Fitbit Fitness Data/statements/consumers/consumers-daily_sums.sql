/*
based on daily values

daily_activity
daily_steps
sleep_day
*/

CREATE TABLE DAILY_SUMS_FITBIT_DATA AS 
    SELECT 
        da.id AS Fitbit_ID,
        SUM(da.tracker_distance) AS Individuals_Total_Tracker_Distance,
        SUM(da.logged_activities_distance) AS Individuals_Total_Logged_Activities_Distance,
        SUM(da.very_active_distance) AS Individuals_Total_Very_Active_Distance,
        SUM(da.moderately_active_distance) AS Individuals_Total_Moderately_Active_Distance,
        SUM(da.light_active_distance) AS Individuals_Total_Light_Active_Distance,
        SUM(da.sedentary_active_distance) AS Individuals_Total_Sedentary_Active_Distance,
        SUM(da.very_active_minutes) AS Individuals_Total_Very_Active_Minutes,
        SUM(da.fairly_active_minutes) AS Individuals_Total_Fairly_Active_Minutes,
        SUM(da.lightly_active_minutes) AS Individuals_Total_Lightly_Active_Minutes,
        SUM(da.sedentary_minutes) AS Individuals_Total_Sedentary_Minutes,
        SUM(da.calories) AS Individuals_Total_Calories,
        COUNT(sd.sleep_day) AS Sleep_Days,
        SUM(sd.total_minutes_asleep) AS Individuals_Total_Time_Asleep_In_Minutes,
        SUM(sd.total_time_in_bed) AS Individuals_Total_Time_In_Bed,
        SUM(ds.step_total) AS Total_Individual_Steps
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
    GROUP BY 
        da.id
    EMIT CHANGES;