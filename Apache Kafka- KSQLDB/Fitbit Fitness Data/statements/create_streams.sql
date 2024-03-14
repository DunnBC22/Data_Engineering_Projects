-- create the minute_METs_narrow stream
CREATE STREAM minute_METs_narrow (
    id BIGINT KEY,
    activity_minute VARCHAR,
    mets INTEGER
)
WITH (
    kafka_topic='minute_METs_narrow', 
    partitions=1, 
    value_format='json'
);

-- create the minute_steps_narrow stream
CREATE STREAM minute_steps_narrow (
    id BIGINT KEY,
    activity_minute VARCHAR,
    num_of_steps INTEGER
)
WITH (
    kafka_topic='minute_steps_narrow', 
    partitions=1, 
    value_format='json'
);

-- create the minute_calories_narrow stream
CREATE STREAM minute_calories_narrow (
    id BIGINT KEY,
    activity_minute VARCHAR,
    calories DOUBLE
)
WITH (
    kafka_topic='minute_calories_narrow', 
    partitions=1, 
    value_format='json'
);

-- create the minute_sleep stream
CREATE STREAM minute_sleep (
    id BIGINT KEY,
    date_and_time VARCHAR,
    sleep_minutes INTEGER,
    log_id BIGINT
)
WITH (
    kafka_topic='minute_sleep', 
    partitions=1, 
    value_format='json'
);

-- create the minute_intensities_narrow stream
CREATE STREAM minute_intensities_narrow (
    id BIGINT KEY,
    activity_minute INTEGER,
    intensity INTEGER
)
WITH (
    kafka_topic='minute_intensities_narrow', 
    partitions=1, 
    value_format='json'
);

-- create the hourly_intensities stream
CREATE STREAM hourly_intensities (
    id BIGINT KEY,
    activity_hour VARCHAR,
    total_intensity INTEGER,
    average_intensity DOUBLE
) 
WITH (
    kafka_topic='hourly_intensities', 
    partitions=4, 
    value_format='json'
);

-- create the hourly_calories stream
CREATE STREAM hourly_calories (
    id BIGINT KEY,
    activity_hour VARCHAR,
    calories INTEGER
) 
WITH (
    kafka_topic='hourly_calories', 
    partitions=4, 
    value_format='json'
);

-- create the hourly_steps stream
CREATE STREAM hourly_steps (
    id BIGINT KEY,
    activity_hour VARCHAR,
    step_total INTEGER
) 
WITH (
    kafka_topic='hourly_steps', 
    partitions=4, 
    value_format='json'
);

-- create the daily_activity stream
CREATE STREAM daily_activity (
    id BIGINT KEY,
    activity_date VARCHAR,
    total_steps DOUBLE,
    total_distance DOUBLE,
    tracker_distance DOUBLE,
    logged_activities_distance DOUBLE,
    very_active_distance DOUBLE,
    moderately_active_distance DOUBLE,
    light_active_distance DOUBLE,
    sedentary_active_distance DOUBLE,
    very_active_minutes INTEGER,
    fairly_active_minutes INTEGER,
    lightly_active_minutes INTEGER,
    sedentary_minutes INTEGER,
    calories INTEGER
) 
WITH (
    kafka_topic='daily_activity', 
    partitions=4, 
    value_format='json'
);

-- create the daily_intensities stream
CREATE STREAM daily_intensities (
    id BIGINT KEY,
    activity_day VARCHAR,
    sedentary_minutes INTEGER,
    lightly_active_minutes INTEGER,
    fairly_active_minutes INTEGER,
    very_active_minutes INTEGER,
    sedentary_active_distance DOUBLE,
    light_active_distance DOUBLE,
    moderately_active_distance DOUBLE,
    very_active_distance DOUBLE
) WITH (
    kafka_topic='daily_intensities', 
    partitions=4,
    value_format='json'
);

-- create the daily_steps stream
CREATE STREAM daily_steps (
    id BIGINT KEY,
    activity_day VARCHAR,
    step_total INTEGER
) WITH (
    kafka_topic='daily_steps', 
    partitions=4,
    value_format='json'
);

-- create the daily_calories stream
CREATE STREAM daily_calories (
    id BIGINT KEY,
    activity_day VARCHAR,
    calories INTEGER
) WITH (
    kafka_topic='daily_calories', 
    partitions=4,
    value_format='json'
);

-- create the sleep_day stream
CREATE STREAM sleep_day (
    id BIGINT KEY,
    sleep_day VARCHAR,
    total_sleep_records INTEGER,
    total_minutes_asleep INTEGER,
    total_time_in_bed INTEGER
)
WITH (
    kafka_topic='sleep_day', 
    partitions=4,
    value_format='json'
);

/*
-- create the minute_calories_wide stream
CREATE STREAM minute_calories_wide (
    id BIGINT KEY,
    activity_hour VARCHAR,
    calories_00 DOUBLE,
    calories_01 DOUBLE,
    calories_02 DOUBLE,
    calories_03 DOUBLE,
    calories_04 DOUBLE,
    calories_05 DOUBLE,
    calories_06 DOUBLE,
    calories_07 DOUBLE,
    calories_08 DOUBLE,
    calories_09 DOUBLE,
    calories_10 DOUBLE,
    calories_11 DOUBLE,
    calories_12 DOUBLE,
    calories_13 DOUBLE,
    calories_14 DOUBLE,
    calories_15 DOUBLE,
    calories_16 DOUBLE,
    calories_17 DOUBLE,
    calories_18 DOUBLE,
    calories_19 DOUBLE,
    calories_20 DOUBLE,
    calories_21 DOUBLE,
    calories_22 DOUBLE,
    calories_23 DOUBLE,
    calories_24 DOUBLE,
    calories_25 DOUBLE,
    calories_26 DOUBLE,
    calories_27 DOUBLE,
    calories_28 DOUBLE,
    calories_29 DOUBLE,
    calories_30 DOUBLE,
    calories_31 DOUBLE,
    calories_32 DOUBLE,
    calories_33 DOUBLE,
    calories_34 DOUBLE,
    calories_35 DOUBLE,
    calories_36 DOUBLE,
    calories_37 DOUBLE,
    calories_38 DOUBLE,
    calories_39 DOUBLE,
    calories_40 DOUBLE,
    calories_41 DOUBLE,
    calories_42 DOUBLE,
    calories_43 DOUBLE,
    calories_44 DOUBLE,
    calories_45 DOUBLE,
    calories_46 DOUBLE,
    calories_47 DOUBLE,
    calories_48 DOUBLE,
    calories_49 DOUBLE,
    calories_50 DOUBLE,
    calories_51 DOUBLE,
    calories_52 DOUBLE,
    calories_53 DOUBLE,
    calories_54 DOUBLE,
    calories_55 DOUBLE,
    calories_56 DOUBLE,
    calories_57 DOUBLE,
    calories_58 DOUBLE,
    calories_59 DOUBLE
) 
WITH (
    kafka_topic='minute_calories_wide', 
    partitions=1, 
    value_format='json'
);

-- create the minute_steps_wide stream
CREATE STREAM minute_steps_wide (
    id BIGINT KEY,
    activity_hour VARCHAR,
    steps_00 DOUBLE,
    steps_01 DOUBLE,
    steps_02 DOUBLE,
    steps_03 DOUBLE,
    steps_04 DOUBLE,
    steps_05 DOUBLE,
    steps_06 DOUBLE,
    steps_07 DOUBLE,
    steps_08 DOUBLE,
    steps_09 DOUBLE,
    steps_10 DOUBLE,
    steps_11 DOUBLE,
    steps_12 DOUBLE,
    steps_13 DOUBLE,
    steps_14 DOUBLE,
    steps_15 DOUBLE,
    steps_16 DOUBLE,
    steps_17 DOUBLE,
    steps_18 DOUBLE,
    steps_19 DOUBLE,
    steps_20 DOUBLE,
    steps_21 DOUBLE,
    steps_22 DOUBLE,
    steps_23 DOUBLE,
    steps_24 DOUBLE,
    steps_25 DOUBLE,
    steps_26 DOUBLE,
    steps_27 DOUBLE,
    steps_28 DOUBLE,
    steps_29 DOUBLE,
    steps_30 DOUBLE,
    steps_31 DOUBLE,
    steps_32 DOUBLE,
    steps_33 DOUBLE,
    steps_34 DOUBLE,
    steps_35 DOUBLE,
    steps_36 DOUBLE,
    steps_37 DOUBLE,
    steps_38 DOUBLE,
    steps_39 DOUBLE,
    steps_40 DOUBLE,
    steps_41 DOUBLE,
    steps_42 DOUBLE,
    steps_43 DOUBLE,
    steps_44 DOUBLE,
    steps_45 DOUBLE,
    steps_46 DOUBLE,
    steps_47 DOUBLE,
    steps_48 DOUBLE,
    steps_49 DOUBLE,
    steps_50 DOUBLE,
    steps_51 DOUBLE,
    steps_52 DOUBLE,
    steps_53 DOUBLE,
    steps_54 DOUBLE,
    steps_55 DOUBLE,
    steps_56 DOUBLE,
    steps_57 DOUBLE,
    steps_58 DOUBLE,
    steps_59 DOUBLE
)
WITH (
    kafka_topic='minute_steps_wide', 
    partitions=10, 
    value_format='json'
);

-- create the minute_intensities_wide stream
CREATE STREAM minute_intensities_wide (
    id BIGINT KEY,
    activity_hour VARCHAR,
    intensity_00 DOUBLE,
    intensity_01 DOUBLE,
    intensity_02 DOUBLE,
    intensity_03 DOUBLE,
    intensity_04 DOUBLE,
    intensity_05 DOUBLE,
    intensity_06 DOUBLE,
    intensity_07 DOUBLE,
    intensity_08 DOUBLE,
    intensity_09 DOUBLE,
    intensity_10 DOUBLE,
    intensity_11 DOUBLE,
    intensity_12 DOUBLE,
    intensity_13 DOUBLE,
    intensity_14 DOUBLE,
    intensity_15 DOUBLE,
    intensity_16 DOUBLE,
    intensity_17 DOUBLE,
    intensity_18 DOUBLE,
    intensity_19 DOUBLE,
    intensity_20 DOUBLE,
    intensity_21 DOUBLE,
    intensity_22 DOUBLE,
    intensity_23 DOUBLE,
    intensity_24 DOUBLE,
    intensity_25 DOUBLE,
    intensity_26 DOUBLE,
    intensity_27 DOUBLE,
    intensity_28 DOUBLE,
    intensity_29 DOUBLE,
    intensity_30 DOUBLE,
    intensity_31 DOUBLE,
    intensity_32 DOUBLE,
    intensity_33 DOUBLE,
    intensity_34 DOUBLE,
    intensity_35 DOUBLE,
    intensity_36 DOUBLE,
    intensity_37 DOUBLE,
    intensity_38 DOUBLE,
    intensity_39 DOUBLE,
    intensity_40 DOUBLE,
    intensity_41 DOUBLE,
    intensity_42 DOUBLE,
    intensity_43 DOUBLE,
    intensity_44 DOUBLE,
    intensity_45 DOUBLE,
    intensity_46 DOUBLE,
    intensity_47 DOUBLE,
    intensity_48 DOUBLE,
    intensity_49 DOUBLE,
    intensity_50 DOUBLE,
    intensity_51 DOUBLE,
    intensity_52 DOUBLE,
    intensity_53 DOUBLE,
    intensity_54 DOUBLE,
    intensity_55 DOUBLE,
    intensity_56 DOUBLE,
    intensity_57 DOUBLE,
    intensity_58 DOUBLE,
    intensity_59 DOUBLE
)
WITH (
    kafka_topic='minute_intensities_wide', 
    partitions=10, 
    value_format='json'
);

-- create the weight_log_info stream
CREATE STREAM weight_log_info (
    id BIGINT KEY,
    date_and_time VARCHAR,
    weight_in_kg DOUBLE,
    weight_in_pounds DOUBLE,
    fat INTEGER,
    bmi DOUBLE,
    is_manual_report BOOLEAN,
    log_dd BIGINT
)
WITH (
    kafka_topic='weight_log_info', 
    partitions=10, 
    value_format='json'
);

-- create the heartrate_seconds stream
CREATE STREAM heartrate_seconds (
    id BIGINT KEY,
    date_and_time VARCHAR,
    heartrate_value INTEGER
) 
WITH (
    kafka_topic='heartrate_seconds', 
    partitions=10, 
    value_format='json'
);
*/