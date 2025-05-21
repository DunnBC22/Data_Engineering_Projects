-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS us_schools_geo_table_pg;

CREATE TABLE us_schools_geo_table_pg (
    "NcesId" INTEGER,
    "SchoolName" VARCHAR,
    "SchoolAddress" VARCHAR,
    "SchoolCity" VARCHAR,
    "SchoolState" VARCHAR,
    "SchoolZipCode" INTEGER,
    "SchoolZipFour" INTEGER,
    "SchoolTelephone" VARCHAR,
    "SchoolType" VARCHAR,
    "SchoolStatus" VARCHAR,
    "DistrictPopulation" INTEGER,
    "SchoolCounty" VARCHAR,
    "CountyFips" VARCHAR,
    "CountryName" VARCHAR,
    "Source" VARCHAR,
    "SourceDate" DATE,
    "ValidationMethod" VARCHAR,
    "ValidationDate" DATE,
    "WebsiteLink" VARCHAR,
    "SchoolLevel" VARCHAR,
    "SchoolEnrollment" INTEGER,
    "StartGrade" VARCHAR,
    "EndGrade" VARCHAR,
    "NumOfFullTimeTeachers" INTEGER,
    "ShelterId" INTEGER,
    "SchoolLocation" VARCHAR
); 