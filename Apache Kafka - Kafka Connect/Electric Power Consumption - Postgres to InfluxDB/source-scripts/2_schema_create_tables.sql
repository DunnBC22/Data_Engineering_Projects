\c epc_db;

CREATE TABLE IF NOT EXISTS epc_table (
    epc_datetime VARCHAR(24),
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    general_diffuse_flows FLOAT,
    diffuse_flows FLOAT,
    power_consumption_zone_1 FLOAT,
    power_consumption_zone_2 FLOAT,
    power_consumption_zone_3 FLOAT
);