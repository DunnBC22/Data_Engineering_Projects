USE gcrd_mariadb_db;

CREATE TABLE IF NOT EXISTS gcrd_mariadb_table (
    `City` VARCHAR(20),
    `Latitude` FLOAT,
    `Longitude` FLOAT,
    `Month` INTEGER,
    `Year` INTEGER,
    `Rainfall (mm)` FLOAT,
    `Elevation (m)` INTEGER,
    `Climate_Type` VARCHAR(20),
    `Temperature (°C)` FLOAT,
    `Humidity (%)` INTEGER
);

