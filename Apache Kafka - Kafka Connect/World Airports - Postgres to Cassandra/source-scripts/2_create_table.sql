\c world_airports_source;
DROP TABLE IF EXISTS world_airports_table;
CREATE TABLE world_airports_table (
    x_coord FLOAT,
    y_coord FLOAT,
    object_id INTEGER,
    id INTEGER PRIMARY KEY,
    airport_identifier VARCHAR(10),
    airport_type VARCHAR(20),
    airport_name VARCHAR(125),
    latitude_coord FLOAT,
    longitude_coord FLOAT,
    elevation_ft INTEGER,
    continent VARCHAR(4),
    iso_country VARCHAR(6),
    iso_region VARCHAR(10),
    municipality VARCHAR(60),
    scheduled_service VARCHAR(8),
    gps_code VARCHAR(8),
    iata_code VARCHAR(8),
    local_code VARCHAR(10),
    home_link VARCHAR(135),
    wikipedia_link VARCHAR(135),
    keywords TEXT,
    communications_desc VARCHAR(70),
    frequency_mhz FLOAT,
    runway_length_ft INTEGER,
    runway_width_ft INTEGER,
    runway_surface VARCHAR(70),
    runway_lighted INTEGER,
    runway_closed INTEGER
);
GRANT SELECT ON world_airports_table TO pg;