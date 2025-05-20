\c flights_db_pg;

DROP TABLE IF EXISTS flights_table_pg;
DROP TABLE IF EXISTS airports_table_pg;

CREATE TABLE flights_table_pg (
    "TransactionId" BIGINT,
    "FlightDate" VARCHAR(20),
    "AirlineCode" VARCHAR(6),
    "TailNumber" VARCHAR(20),
    "FlightNumber" INTEGER,
    "OriginAirportCode" VARCHAR(6),
    "DestinationAirportCode" VARCHAR(6),
    "CrsDepartureTime" INTEGER,
    "DepartureTime" INTEGER,
    "DepartureDelay" INTEGER,
    "TaxiOut" INTEGER,
    "WheelsOff" INTEGER,
    "WheelsOn" INTEGER,
    "TaxiIn" INTEGER,
    "CrsArrivalTime" INTEGER,
    "ArrivalTime" INTEGER,
    "ArrivalDelay" INTEGER,
    "CrsElapsedTime" INTEGER,
    "ActualElapsedTime" INTEGER,
    "FlightCancelled" VARCHAR(20),
    "FlightDiverted" VARCHAR(20),
    "FlightDistance" INTEGER,
    "FlightDate_DayOfWeek" INTEGER,
    "FlightDate_DayOfMonth" INTEGER,
    "FlightDate_DayOfYear" INTEGER,
    "FlightDate_Month" INTEGER,
    "FlightDate_Quarter" INTEGER,
    "FlightDate_Year" INTEGER
);

CREATE TABLE airports_table_pg (
    "AirportCode" VARCHAR(6) PRIMARY KEY,
    "AirportCityName" VARCHAR(80),
    "AirportState" VARCHAR(6),
    "AirportName" VARCHAR(100),
    "AirportStateName" VARCHAR(80)
);