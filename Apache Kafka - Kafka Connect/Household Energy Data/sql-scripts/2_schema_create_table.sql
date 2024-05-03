\c hh_nrg_db;

DROP TABLE IF EXISTS household_energy_data;
CREATE TABLE household_energy_data (hh_nrg_id INTEGER PRIMARY KEY NOT NULL,energy_type VARCHAR,energy_date VARCHAR,start_time VARCHAR,end_time VARCHAR,energy_usage INTEGER,energy_units VARCHAR,energy_cost VARCHAR,notes VARCHAR);
GRANT SELECT ON household_energy_data TO pg;