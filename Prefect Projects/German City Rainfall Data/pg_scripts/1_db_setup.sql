-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

\c gcrd_db_pg;

DROP TABLE IF EXISTS gcrd_table_pg;

CREATE TABLE gcrd_table_pg (
    RecordedCity VARCHAR(20),
    RecordedLatitude FLOAT,
    RecordedLongitude FLOAT,
    RecordedMonth INTEGER,
    RecordedYear INTEGER,
    RainfallInMillimeters FLOAT,
    ElevationInMeters INTEGER,
    ClimateType VARCHAR(16),
    TemperatureInCelsius FLOAT,
    HumidityPercent INTEGER
);