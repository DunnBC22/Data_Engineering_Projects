-- Make sure that the data is imported into the postgres tables correctly (run this in bash, not the docker CLI)
-- For selecting data from Postgres
echo 'SELECT * FROM car_specs LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'
-- For counting rows in Postgres
echo 'SELECT COUNT(id) AS Num_Of_Records FROM car_specs;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER $POSTGRES_DB'

/*
#docker compose command to develop interactively:

docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
*/

-- update the auto.offset.reset setting
SET 'auto.offset.reset' = 'earliest';

-- CREATE SOURCE CONNECTORs
CREATE SOURCE CONNECTOR IF NOT EXISTS PG_CARS_DATA_STREAM_SOURCE_CONN WITH (
    'name' = 'source connector to retrieve records from postgres car_specs table in cars_data db',
    'connector.class' = 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url' = 'jdbc:postgresql://postgres:5432/cars_data',
    'dialect.name' = 'PostgreSqlDatabaseDialect',
    'connection.user' = 'pg',
    'connection.password' = 'pg',
    'incrementing.column.name' = 'id',
    'table.whitelist' = 'car_specs', 
    'topic.prefix' = 'pg_',
    'errors.log.enable' = 'true',
    'tasks.max' = 1,
    'mode'='incrementing',
    'numeric.mapping' = 'best_fit',
    'poll.interval.ms' = 360000,
    'batch.max.rows' = 15000,
    'transforms' = 'copyFieldToKey,extractKeyFromStruct,removeKeyFromValue',
    'transforms.copyFieldToKey.type' = 'org.apache.kafka.connect.transforms.ValueToKey',
    'transforms.copyFieldToKey.fields' = 'id',
    'transforms.extractKeyFromStruct.type' = 'org.apache.kafka.connect.transforms.ExtractField$Key',
    'transforms.extractKeyFromStruct.field' = 'id',
    'transforms.removeKeyFromValue.type' = 'org.apache.kafka.connect.transforms.ReplaceField$Value',
    'transforms.removeKeyFromValue.blacklist' = 'id',
    'key.converter' = 'org.apache.kafka.connect.converters.IntegerConverter'
);

SHOW CONNECTORS;
DESCRIBE CONNECTOR PG_CARS_DATA_STREAM_SOURCE_CONN;

CREATE STREAM CAR_SPECS (
    id INTEGER KEY,
    model VARCHAR(84),
    serie VARCHAR(42),
    company VARCHAR(26),
    body_style VARCHAR(67),
    segment VARCHAR(24),
    production_years VARCHAR,
    cylinders VARCHAR(79),
    displacement VARCHAR(12),
    power_hp VARCHAR(27),
    power_bhp VARCHAR(28),
    power_kw VARCHAR(29),
    torque_lb_ft VARCHAR(30),
    torque_nm VARCHAR(27),
    electrical_motor_power VARCHAR(21),
    electrical_motor_torque VARCHAR(24),
    fuel_system VARCHAR(198),
    fuel VARCHAR(31),
    fuel_capacity VARCHAR(25),
    top_speed VARCHAR(29),
    acceleration_0_62 VARCHAR(13),
    drive_type VARCHAR(19),
    gearbox VARCHAR(154),
    front_brake VARCHAR(91),
    rear_brake VARCHAR(91),
    tire_size VARCHAR(66),
    car_length VARCHAR(35),
    car_width VARCHAR(26),
    car_height VARCHAR(26),
    front_rear_track VARCHAR(35),
    wheelbase VARCHAR(35),
    ground_clearance VARCHAR(29),
    aerodynamics_cd VARCHAR(11),
    aerodynamics_frontal_area VARCHAR(9),
    turning_circle VARCHAR(20),
    cargo_volume VARCHAR(28),
    unladen_weight VARCHAR(36),
    gross_weight_limit VARCHAR(36),
    combined_mpg VARCHAR(29),
    city_mpg VARCHAR(29),
    highway_mpg VARCHAR(29),
    co2_emissions VARCHAR(66),
    co2_emissions_combined VARCHAR(10),
    turning_circle_curb_to_curb VARCHAR(19),
    total_max_power VARCHAR(25),
    power_pack VARCHAR(67),
    nominal_capacity VARCHAR(11),
    top_speed_electrical VARCHAR(20),
    ev_range VARCHAR(26),
    high_mpg VARCHAR(28),
    extra_high_mpg VARCHAR(28),
    medium_mpg VARCHAR(28),
    low_mpg VARCHAR(28),
    total_max_torque VARCHAR(24),
    max_capacity VARCHAR(11),
    spec_summary VARCHAR(60)
) 
WITH 
(
    KAFKA_TOPIC='pg_car_specs', 
    VALUE_FORMAT='AVRO',
    partitions=1
);

-- Create intermediate & sink STREAMs
-- all data for all vehicles
CREATE STREAM ALL_FEATURES_OF_ALL_VEHICLES AS 
    SELECT 
        id AS ID,
        company AS Manufacturer,
        model AS Vehicle_Model,
        serie AS Vehicle_Series,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        production_years AS Production_Years,
        cylinders AS Number_of_Cylinders_Engine,
        displacement AS Engine_Displacement,
        power_hp AS Power_HP,
        power_bhp AS Power_BHP,
        power_kw AS Power_KW,
        torque_lb_ft AS Torque_LB_FT,
        torque_nm AS Torque_NM,
        electrical_motor_power AS Electrical_Motor_Power,
        electrical_motor_torque AS Electrical_Motor_Torque,
        fuel_system AS Fuel_System,
        fuel AS Fuel,
        fuel_capacity AS Fuel_Capacity,
        top_speed AS Top_Speed,
        acceleration_0_62 AS Acceleration_0_62,
        drive_type AS Drive_Type,
        gearbox AS Gearbox,
        front_brake AS Front_Brake,
        rear_brake AS Rear_Brake,
        tire_size AS Tire_Size,
        car_length AS Car_Length,
        car_width AS Car_Width,
        car_height AS Car_Height,
        front_rear_track AS Front_Rear_Track,
        wheelbase AS Wheelbase,
        ground_clearance AS Ground_Clearnace,
        turning_circle AS Turning_Radius,
        cargo_volume AS Cargo_Volume,
        gross_weight_limit AS Gross_Weight_Limit,
        combined_mpg AS Combined_MPG,
        city_mpg AS City_MPG,
        highway_mpg AS Highway_MPG,
        co2_emissions AS CO2_Emissions,
        co2_emissions_combined AS CO2_Emissions_Combined,
        turning_circle_curb_to_curb AS Turning_Circle_Curb_To_Curb,
        total_max_power AS Total_Max_Power,
        power_pack AS Power_Pack,
        nominal_capacity AS Nominal_Capacity,
        top_speed_electrical AS Top_Speed_Electrical,
        ev_range AS EV_Range,
        aerodynamics_cd AS Aerodynamics_CD,
        aerodynamics_frontal_area AS Aerodynamics_Frontal_Area,
        unladen_weight AS Unladen_Weight,
        high_mpg AS High_MPG,
        extra_high_mpg AS Extra_High_MPG,
        medium_mpg AS Medium_MPG,
        low_mpg AS Low_MPG,
        total_max_torque AS Total_Max_Torque,
        max_capacity AS Max_Capacity,
        spec_summary AS Spec_Summary
    FROM 
        car_specs
    EMIT CHANGES;

-- main features for all vehicles
CREATE STREAM MAIN_FEATURES_OF_ALL_VEHICLES AS 
    SELECT 
        id AS ID,
        company AS Manufacturer,
        model AS Vehicle_Model,
        serie AS Vehicle_Series,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        production_years AS Production_Years,
        cylinders AS Number_of_Cylinders_Engine,
        displacement AS Engine_Displacement,
        power_hp AS Power_HP,
        power_bhp AS Power_BHP,
        power_kw AS Power_KW,
        torque_lb_ft AS Torque_LB_FT,
        torque_nm AS Torque_NM,
        electrical_motor_power AS Electrical_Motor_Power,
        electrical_motor_torque AS Electrical_Motor_Torque,
        fuel_system AS Fuel_System,
        fuel AS Fuel,
        fuel_capacity AS Fuel_Capacity,
        top_speed AS Top_Speed,
        acceleration_0_62 AS Acceleration_0_62,
        drive_type AS Drive_Type,
        gearbox AS Gearbox,
        front_brake AS Front_Brake,
        rear_brake AS Rear_Brake,
        tire_size AS Tire_Size,
        car_length AS Car_Length,
        car_width AS Car_Width,
        car_height AS Car_Height,
        front_rear_track AS Front_Rear_Track,
        wheelbase AS Wheelbase,
        ground_clearance AS Ground_Clearnace,
        turning_circle AS Turning_Radius,
        cargo_volume AS Cargo_Volume,
        gross_weight_limit AS Gross_Weight_Limit,
        combined_mpg AS Combined_MPG,
        city_mpg AS City_MPG,
        highway_mpg AS Highway_MPG,
        co2_emissions AS CO2_Emissions,
        co2_emissions_combined AS CO2_Emissions_Combined,
        turning_circle_curb_to_curb AS Turning_Circle_Curb_To_Curb,
        total_max_power AS Total_Max_Power,
        power_pack AS Power_Pack,
        nominal_capacity AS Nominal_Capacity,
        top_speed_electrical AS Top_Speed_Electrical,
        ev_range AS EV_Range
    FROM 
        car_specs
    EMIT CHANGES;

-- physical dimensions only of each vehicle
CREATE STREAM PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES AS 
    SELECT 
        id AS ID,
        company AS Manufacturer,
        model AS Vehicle_Model,
        serie AS Vehicle_Series,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        production_years AS Production_Years,
        tire_size AS Tire_Size,
        car_length AS Car_Length,
        car_width AS Car_Width,
        car_height AS Car_Height,
        wheelbase AS Wheelbase,
        ground_clearance AS Ground_Clearnace,
        turning_circle AS Turning_Radius,
        cargo_volume AS Cargo_Volume,
        gross_weight_limit AS Gross_Weight_Limit,
        turning_circle_curb_to_curb AS Turning_Circle_Curb_To_Curb
    FROM 
        car_specs
    EMIT CHANGES;

-- engine type, size and output only for each vehicle
CREATE STREAM VEHICLE_ENGINE_AND_OUTPUT_SPECS AS 
    SELECT
        id AS ID, 
        company AS Manufacturer,
        model AS Vehicle_Model,
        serie AS Vehicle_Series,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        production_years AS Production_Years,
        cylinders AS Number_of_Cylinders_Engine,
        displacement AS Engine_Displacement,
        power_hp AS Power_HP,
        power_bhp AS Power_BHP,
        power_kw AS Power_KW,
        torque_lb_ft AS Torque_LB_FT,
        torque_nm AS Torque_NM,
        electrical_motor_power AS Electrical_Motor_Power,
        electrical_motor_torque AS Electrical_Motor_Torque,
        fuel_system AS Fuel_System,
        fuel AS Fuel,
        fuel_capacity AS Fuel_Capacity,
        top_speed AS Top_Speed,
        acceleration_0_62 AS Acceleration_0_62,
        total_max_power AS Total_Max_Power,
        power_pack AS Power_Pack,
        nominal_capacity AS Nominal_Capacity,
        top_speed_electrical AS Top_Speed_Electrical,
        ev_range AS EV_Range
    FROM 
        car_specs
    EMIT CHANGES;

-- fuel economy features only for each vehicle
CREATE STREAM FUEL_AND_ELECTRICITY_ECONOMY_SPECS AS 
    SELECT 
        id AS ID,
        company AS Manufacturer,
        model AS Vehicle_Model,
        serie AS Vehicle_Series,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        production_years AS Production_Years,
        fuel_system AS Fuel_System,
        fuel AS Fuel,
        fuel_capacity AS Fuel_Capacity,
        combined_mpg AS Combined_MPG,
        city_mpg AS City_MPG,
        highway_mpg AS Highway_MPG,
        total_max_power AS Total_Max_Power,
        power_pack AS Power_Pack,
        nominal_capacity AS Nominal_Capacity,
        top_speed_electrical AS Top_Speed_Electrical,
        ev_range AS EV_Range
    FROM 
        car_specs
    EMIT CHANGES;


-- only return main data for vehicles in the 'Coupe' segment
CREATE STREAM MAIN_DATA_FOR_COUPES AS 
    SELECT
        id AS ID,
        company AS Manufacturer,
        model AS Vehicle_Model,
        serie AS Vehicle_Series,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        production_years AS Production_Years,
        cylinders AS Number_of_Cylinders_Engine,
        displacement AS Engine_Displacement,
        power_hp AS Power_HP,
        power_bhp AS Power_BHP,
        power_kw AS Power_KW,
        torque_lb_ft AS Torque_LB_FT,
        torque_nm AS Torque_NM,
        electrical_motor_power AS Electrical_Motor_Power,
        electrical_motor_torque AS Electrical_Motor_Torque,
        fuel_system AS Fuel_System,
        fuel AS Fuel,
        fuel_capacity AS Fuel_Capacity,
        top_speed AS Top_Speed,
        acceleration_0_62 AS Acceleration_0_62,
        drive_type AS Drive_Type,
        gearbox AS Gearbox,
        front_brake AS Front_Brake,
        rear_brake AS Rear_Brake,
        tire_size AS Tire_Size,
        car_length AS Car_Length,
        car_width AS Car_Width,
        car_height AS Car_Height,
        front_rear_track AS Front_Rear_Track,
        wheelbase AS Wheelbase,
        ground_clearance AS Ground_Clearnace,
        turning_circle AS Turning_Radius,
        cargo_volume AS Cargo_Volume,
        gross_weight_limit AS Gross_Weight_Limit,
        combined_mpg AS Combined_MPG,
        city_mpg AS City_MPG,
        highway_mpg AS Highway_MPG,
        co2_emissions AS CO2_Emissions,
        co2_emissions_combined AS CO2_Emissions_Combined,
        turning_circle_curb_to_curb AS Turning_Circle_Curb_To_Curb,
        total_max_power AS Total_Max_Power,
        power_pack AS Power_Pack,
        nominal_capacity AS Nominal_Capacity,
        top_speed_electrical AS Top_Speed_Electrical,
        ev_range AS EV_Range
    FROM 
        car_specs
    WHERE
        segment LIKE '%Coupe%'
    EMIT CHANGES;

CREATE STREAM ACURA_CAR_SPECS AS 
    SELECT
        id AS Record_ID,
        model AS Model,
        serie AS Car_Series,
        company AS Manufacturer,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        cylinders AS Number_of_Cylinders,
        fuel_system AS Vehicle_Fuel_System,
        fuel AS Fuel,
        drive_type AS Vehicle_Drive_Type,
        gearbox AS Gearbox,
        turning_circle AS Turning_Circle,
        cargo_volume AS Cargo_Volume
    FROM
        car_specs
    WHERE
        model LIKE '%ACURA%'
    OR 
        model LIKE '%Acura%'
    OR 
        model LIKE '%acura%'
    EMIT CHANGES;

SHOW TOPICS;
SHOW STREAMS;

-- DESCRIBE STREAMS
DESCRIBE ALL_FEATURES_OF_ALL_VEHICLES EXTENDED;
DESCRIBE MAIN_FEATURES_OF_ALL_VEHICLES EXTENDED;
DESCRIBE PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES EXTENDED;
DESCRIBE VEHICLE_ENGINE_AND_OUTPUT_SPECS EXTENDED;
DESCRIBE FUEL_AND_ELECTRICITY_ECONOMY_SPECS EXTENDED;
DESCRIBE MAIN_DATA_FOR_COUPES EXTENDED;
DESCRIBE ACURA_CAR_SPECS EXTENDED;

-- CREATE SINK CONNECTORs
CREATE SINK CONNECTOR IF NOT EXISTS PG_ALL_FEATURES_OF_ALL_VEHICLES_STREAM_SINK_CONN WITH (
  'name'                = 'pg_all_features_of_all_vehicles_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'dialect.name'        = 'PostgreSqlDatabaseDialect',
  'topics'              = 'ALL_FEATURES_OF_ALL_VEHICLES',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS PG_ACURA_CAR_SPECS_STREAM_SINK_CONN WITH (
  'name'                = 'pg_acura_car_specs_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'ACURA_CAR_SPECS',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS PG_FUEL_AND_ELECTRICITY_ECONOMY_SPECS_STREAM_SINK_CONN WITH (
  'name'                = 'pg_fuel_and_electricity_economy_specs_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'FUEL_AND_ELECTRICITY_ECONOMY_SPECS',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS PG_MAIN_FEATURES_OF_ALL_VEHICLES_STREAM_SINK_CONN WITH (
  'name'                = 'pg_main_features_of_all_vehicles_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'MAIN_FEATURES_OF_ALL_VEHICLES',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS PG_MAIN_DATA_FOR_COUPES_STREAM_SINK_CONN WITH (
  'name'                = 'pg_main_data_for_coupes_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'MAIN_DATA_FOR_COUPES',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS PG_PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES_STREAM_SINK_CONN WITH (
  'name'                = 'pg_physical_dimensions_of_all_vehicles_stream_sink_conn',
  'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
  'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
  'connection.user'     = 'pg',
  'connection.password' = 'pg',
  'output.data.format'  = 'avro',
  'topics'              = 'PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES',
  'auto.create'         = 'true',
  'auto.evolve'         = 'true',
  'table.name.format'   = 'output_${topic}'
);

CREATE SINK CONNECTOR IF NOT EXISTS PG_VEHICLE_ENGINE_AND_OUTPUT_SPECS_STREAM_SINK_CONN WITH (
    'name'                = 'pg_vehicle_engine_and_output_specs_stream_sink_conn',
    'connector.class'     = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    'connection.url'      = 'jdbc:postgresql://postgres:5432/output_tables',
    'connection.user'     = 'pg',
    'connection.password' = 'pg',
    'output.data.format'  = 'avro',
    'topics'              = 'VEHICLE_ENGINE_AND_OUTPUT_SPECS',
    'auto.create'         = 'true',
    'auto.evolve'         = 'true',
    'table.name.format'   = 'output_${topic}'
);

-- other statements
SHOW CONNECTORS;
SHOW TOPICS;
SHOW STREAMS;
SHOW TABLES;
SHOW PROPERTIES;
SHOW QUERIES;

-- DESCRIBE components (streams, tables, and connectors)
-- source connectors
DESCRIBE CONNECTOR PG_CARS_DATA_STREAM_SOURCE_CONN;

DESCRIBE car_specs EXTENDED;
PRINT 'pg_car_specs' FROM BEGINNING LIMIT 5;
PRINT 'ACURA_CAR_SPECS' FROM BEGINNING LIMIT 5;
PRINT 'FUEL_AND_ELECTRICITY_ECONOMY_SPECS' FROM BEGINNING LIMIT 5;
PRINT 'MAIN_DATA_FOR_COUPES' FROM BEGINNING LIMIT 5;

-- sink connectors
DESCRIBE CONNECTOR PG_MAIN_DATA_FOR_COUPES_STREAM_SINK_CONN;
DESCRIBE CONNECTOR PG_VEHICLE_ENGINE_AND_OUTPUT_SPECS_STREAM_SINK_CONN;
DESCRIBE CONNECTOR PG_PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES_STREAM_SINK_CONN;
DESCRIBE CONNECTOR PG_ACURA_CAR_SPECS_STREAM_SINK_CONN;
DESCRIBE CONNECTOR PG_MAIN_FEATURES_OF_ALL_VEHICLES_STREAM_SINK_CONN;
DESCRIBE CONNECTOR PG_ALL_FEATURES_OF_ALL_VEHICLES_STREAM_SINK_CONN;
DESCRIBE CONNECTOR PG_FUEL_AND_ELECTRICITY_ECONOMY_SPECS_STREAM_SINK_CONN;

-- Run these scripts to make sure that the data successfully made its way to the target database
-- all_features_of_all_vehicles
echo 'SELECT * FROM "output_ALL_FEATURES_OF_ALL_VEHICLES" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_ALL_FEATURES_OF_ALL_VEHICLES";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'

-- ACURA_CAR_SPECS
echo 'SELECT * FROM "output_ACURA_CAR_SPECS" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_ACURA_CAR_SPECS";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'

-- fuel_and_electricity_economy_specs
echo 'SELECT * FROM "output_FUEL_AND_ELECTRICITY_ECONOMY_SPECS" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_FUEL_AND_ELECTRICITY_ECONOMY_SPECS";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'

-- main_features_of_all_vehicles
echo 'SELECT * FROM "output_MAIN_FEATURES_OF_ALL_VEHICLES" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_MAIN_FEATURES_OF_ALL_VEHICLES";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'

-- main_data_for_coupes
echo 'SELECT * FROM "output_MAIN_DATA_FOR_COUPES" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_MAIN_DATA_FOR_COUPES";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'

-- physical_dimensions_of_all_vehicles
echo 'SELECT * FROM "output_PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'

-- vehicle_engine_and_output_specs
echo 'SELECT * FROM "output_VEHICLE_ENGINE_AND_OUTPUT_SPECS" LIMIT 25;' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'
echo 'SELECT COUNT("MANUFACTURER") FROM "output_VEHICLE_ENGINE_AND_OUTPUT_SPECS";' | docker exec -i postgres bash -c 'psql -U $POSTGRES_USER output_tables'


-- DROP CONNECTORS
-- SINK CONNECTORS
DROP CONNECTOR PG_VEHICLE_ENGINE_AND_OUTPUT_SPECS_STREAM_SINK_CONN;
DROP CONNECTOR PG_PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES_STREAM_SINK_CONN;
DROP CONNECTOR PG_ACURA_CAR_SPECS_STREAM_SINK_CONN;
DROP CONNECTOR PG_MAIN_FEATURES_OF_ALL_VEHICLES_STREAM_SINK_CONN;
DROP CONNECTOR PG_ALL_FEATURES_OF_ALL_VEHICLES_STREAM_SINK_CONN;
DROP CONNECTOR PG_MAIN_DATA_FOR_COUPES_STREAM_SINK_CONN;
DROP CONNECTOR PG_FUEL_AND_ELECTRICITY_ECONOMY_SPECS_STREAM_SINK_CONN;

-- SOURCE CONNECTOR(s)
DROP CONNECTOR PG_CARS_DATA_STREAM_SOURCE_CONN;

-- DROP STREAM(s) &/or TABLE(s)
DROP STREAM IF EXISTS ACURA_CAR_SPECS DELETE TOPIC;
DROP STREAM IF EXISTS ALL_FEATURES_OF_ALL_VEHICLES DELETE TOPIC;
DROP STREAM IF EXISTS FUEL_AND_ELECTRICITY_ECONOMY_SPECS DELETE TOPIC;
DROP STREAM IF EXISTS MAIN_DATA_FOR_COUPES DELETE TOPIC;
DROP STREAM IF EXISTS MAIN_FEATURES_OF_ALL_VEHICLES DELETE TOPIC;
DROP STREAM IF EXISTS PHYSICAL_DIMENSIONS_OF_ALL_VEHICLES DELETE TOPIC;
DROP STREAM IF EXISTS VEHICLE_ENGINE_AND_OUTPUT_SPECS DELETE TOPIC;

DROP STREAM IF EXISTS CAR_SPECS DELETE TOPIC;