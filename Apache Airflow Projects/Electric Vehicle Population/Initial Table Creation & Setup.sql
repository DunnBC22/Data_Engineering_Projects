-- database name: ev_population_db
-- owner: airflow

CREATE TABLE ev_population (
    VIN VARCHAR,
    County VARCHAR,
    City VARCHAR,
    StateName VARCHAR,
    PostalCode INTEGER,
    ModelYear INTEGER,
    Make VARCHAR,
    Model VARCHAR,
    ElectricVehicleType VARCHAR,
    CAFVEligibility VARCHAR,
    ElectricRange INTEGER,
    BaseMSRP INTEGER,
    LegislativeDistrict INTEGER,
    DOLVehicleID INTEGER,
    VehicleLocation VARCHAR,
    ElectricUtility VARCHAR,
    CensusTract2020 BIGINT
);

COPY ev_population(
    VIN,
    County,
    City,
    StateName,
    PostalCode,
    ModelYear,
    Make,
    Model,
    ElectricVehicleType,
    CAFVEligibility,	
    ElectricRange,
    BaseMSRP,
    LegislativeDistrict,
    DOLVehicleID,
    VehicleLocation,
    ElectricUtility,
    CensusTract2020
    )
FROM '/Users/briandunn/Desktop/Projects 2/Electric Vehicle Population/Electric_Vehicle_Population_Data.csv'
DELIMITER ','
CSV HEADER;