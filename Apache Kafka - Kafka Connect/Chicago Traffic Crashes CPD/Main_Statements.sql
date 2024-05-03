-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
echo 'SELECT * FROM cpd_traffic_crashes LIMIT 12;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
echo 'SELECT COUNT(crash_record_id) FROM cpd_traffic_crashes;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- CREATE SOURCE CONNECTOR(s)
CREATE SOURCE CONNECTOR IF NOT EXISTS pg_cpd_traffic_crashes_stream_source_conn WITH (
    'name' = 'source_connector_to_pg_stream_of_traffic_crashes_from_chicago_police_department',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/cpd_traffic_crashes_db',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'mode' = 'incrementing',
    'topic.prefix' = 'pg_',
    'incrementing.column.name' = 'crash_record_id',
    'table.whitelist' = 'cpd_traffic_crashes',
    'validate.non.null' = true,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'crash_record_id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'crash_record_id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'crash_record_id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

CREATE STREAM cpd_traffic_crashes (
    crash_record_id VARCHAR,
    crash_date_est_i VARCHAR,
    crash_date VARCHAR,
    posted_speed_limit INTEGER,
    traffic_control_device VARCHAR,
    device_condition VARCHAR,
    weather_condition VARCHAR,
    lighting_condition VARCHAR,
    first_crash_type VARCHAR,
    trafficway_type VARCHAR,
    lane_cnt INTEGER,
    alignment VARCHAR,
    roadway_surface_cond VARCHAR,
    road_defect VARCHAR,
    report_type VARCHAR,
    crash_type VARCHAR,
    intersection_related_i VARCHAR,
    not_right_of_way_i VARCHAR,
    hit_and_run_i VARCHAR,
    damage VARCHAR,
    date_police_notified VARCHAR,
    prim_contributory_cause VARCHAR,
    sec_contributory_cause VARCHAR,
    street_num INTEGER,
    street_direction VARCHAR,
    street_name VARCHAR,
    beat_of_occurence INTEGER,
    photos_taken_i VARCHAR,
    statements_taken_i VARCHAR,
    dooring_i VARCHAR,
    work_zone_i VARCHAR,
    work_zone_type VARCHAR,
    workers_present_i VARCHAR,
    num_units INTEGER,
    most_severe_injury VARCHAR,
    injuries_total INTEGER,
    injuries_fatal INTEGER,
    injuries_incapacitating INTEGER,
    injuries_non_incapacitating INTEGER,
    injuries_reported_not_evident INTEGER,
    injuries_no_indication INTEGER,
    injuries_unknown INTEGER,
    crash_hour INTEGER,
    crash_day_of_week INTEGER,
    crash_month INTEGER,
    latitude DOUBLE,
    longitude DOUBLE,
    crash_location VARCHAR
)
WITH 
(
    KAFKA_TOPIC = 'pg_cpd_traffic_crashes', 
    VALUE_FORMAT = 'AVRO',
    PARTITIONS = 1
);

-- Create intermediate & sink STREAMs
CREATE STREAM cleaned_cpd_traffic_crashes 
WITH 
(
    KAFKA_TOPIC = 'cleaned_cpd_traffic_crashes',
    VALUE_FORMAT = 'AVRO',
    PARTITIONS = 1
)
AS
    SELECT
        crash_record_id AS Crash_Record_Id,
        crash_date_est_i AS Crash_Date_Estimated_Indicator,
        PARSE_DATE(SPLIT(crash_date, ' ')[1], 'MM/DD/yyyy') AS Crash_Date,
        SUBSTRING(crash_date, 12) AS Crash_Time_of_Day,
        CASE
            WHEN SPLIT(crash_date, ' ')[-1] = 'AM' THEN 
                CASE
                    WHEN 
                        SUBSTRING(crash_date, 12, 2) = '12'
                    THEN 
                        '00'
                    ELSE 
                        SUBSTRING(crash_date, 12, 2)
                END
            WHEN SPLIT(crash_date, ' ')[-1] = 'PM' THEN
                CASE
                    WHEN 
                        SUBSTRING(crash_date, 12, 2) = '12'
                    THEN 
                        '12'
                    ELSE 
                        CAST((CAST(SUBSTRING(crash_date, 12, 2) AS INTEGER) + 12) AS VARCHAR)
                END
        END AS hour_part,
        SUBSTRING(crash_date, 15, 2) AS minute_part,
        SUBSTRING(crash_date, 18, 2) AS second_part,
        posted_speed_limit AS Posted_Speed_Limit,
        TRIM(traffic_control_device) AS Traffic_control_device,
        TRIM(device_condition) AS Device_Condition,
        TRIM(weather_condition) AS Weather_Condition,
        TRIM(lighting_condition) AS Lighting_Condition,
        TRIM(first_crash_type) AS First_Crash_Type,
        TRIM(trafficway_type) AS Trafficway_Type,
        lane_cnt AS Lane_Count,
        TRIM(alignment) AS Alignment,
        TRIM(roadway_surface_cond) AS Roadway_Surface_Condition,
        TRIM(road_defect) AS Road_Defect,
        TRIM(report_type) AS Report_Type,
        TRIM(crash_type) AS Crash_Type,
        intersection_related_i AS Intersection_Related_Indicator,
        not_right_of_way_i AS Not_Right_Of_Way_Indicator,
        hit_and_run_i AS Hit_And_Run_Indicator,
        TRIM(damage) AS Damage,
        PARSE_DATE(SPLIT(date_police_notified, ' ')[1], 'MM/DD/yyyy') AS Date_Police_Notified,
        SUBSTRING(date_police_notified, 12) AS time_of_day_police_notified,
        CASE
            WHEN SPLIT(date_police_notified, ' ')[-1] = 'AM' THEN 
                CASE
                    WHEN 
                        SUBSTRING(date_police_notified, 12, 2) = '12' 
                    THEN 
                        '00'
                    ELSE 
                        SUBSTRING(date_police_notified, 12, 2)
                END
            WHEN SPLIT(date_police_notified, ' ')[-1] = 'PM' THEN
                CASE
                    WHEN 
                        SUBSTRING(date_police_notified, 12, 2) = '12' 
                    THEN 
                        '12'
                    ELSE 
                        CAST((CAST(SUBSTRING(date_police_notified, 12, 2) AS INTEGER) + 12) AS VARCHAR)
                END
        END AS pn_hour_part,
        SUBSTRING(date_police_notified, 15, 2) AS pn_minute_part,
        SUBSTRING(date_police_notified, 18, 2) AS pn_second_part,
        TRIM(prim_contributory_cause) AS Primary_Contributory_Cause,
        TRIM(sec_contributory_cause) AS Secondary_Contributory_Cause,
        street_num AS Street_Number,
        TRIM(street_direction) AS Street_Direction,
        TRIM(street_name) AS Street_Name,
        beat_of_occurence AS Beat_Of_Occurence,
        photos_taken_i AS Photos_Taken_Indicator,
        statements_taken_i AS Statements_Taken_Indicator,
        dooring_i AS dooring_Indicator,
        work_zone_i AS Work_Zone_Indicator,
        TRIM(work_zone_type) AS Work_Zone_Type,
        workers_present_i AS Workers_Present_Indicator,
        num_units AS Num_Units_Involved_In_Crash,
        TRIM(most_severe_injury) AS Most_Severe_Injury,
        injuries_total AS Injuries_Total,
        injuries_fatal AS Injuries_Fatal,
        injuries_incapacitating AS Injuries_Incapacitating,
        injuries_non_incapacitating AS Injuries_Non_Incapacitating,
        injuries_reported_not_evident AS Injuries_Reported_Not_Evident,
        injuries_no_indication AS Injuries_No_Indication,
        injuries_unknown AS Injuries_Unknown,
        crash_hour AS Crash_Hour,
        crash_day_of_week AS Crash_Day_of_Week,
        crash_month AS Crash_Month,
        latitude AS Latitude_Of_Crash,
        longitude AS Longitude_Of_Crash,
        TRIM(crash_location) AS Crash_Location
    FROM 
        cpd_traffic_crashes
    EMIT CHANGES; 

SHOW TOPICS;
SHOW STREAMS;

-- DESCRIBE STREAMS
DESCRIBE cleaned_cpd_traffic_crashes EXTENDED;

-- CREATE SINK CONNECTORs
CREATE SINK CONNECTOR IF NOT EXISTS pg_cpd_traffic_crashes_stream_sink_conn WITH (
  'name'                = 'sink_connector_for_cleaned_chicago_police_dep_traffic_crashes_data',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_cpd_traffic_crashes_db',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'AVRO',
  'topics'              = 'cleaned_cpd_traffic_crashes',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true'
);

-- Run these scripts to make sure that the data successfully made its way to the target database
-- all_features_of_all_vehicles
echo 'SELECT * FROM "cleaned_cpd_traffic_crashes" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_cpd_traffic_crashes_db'
echo 'SELECT COUNT("CRASH_DATE") FROM "cleaned_cpd_traffic_crashes";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_cpd_traffic_crashes_db'

-- other statements
SHOW TOPICS;
SHOW STREAMS;
SHOW CONNECTORS;

-- DESCRIBE components (streams, tables, and connectors)
-- source connectors
DESCRIBE CONNECTOR pg_cpd_traffic_crashes_stream_source_conn;

-- sink connectors
DESCRIBE CONNECTOR pg_cpd_traffic_crashes_stream_sink_conn;

DESCRIBE cpd_traffic_crashes EXTENDED;