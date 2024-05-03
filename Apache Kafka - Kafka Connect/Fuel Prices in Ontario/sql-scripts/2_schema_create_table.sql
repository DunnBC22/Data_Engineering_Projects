\c ontario_fuel_prices_db;

DROP TABLE IF EXISTS ontario_fuel_prices;
CREATE TABLE ontario_fuel_prices (gas_price_id INTEGER PRIMARY KEY NOT NULL,gas_price_date VARCHAR,ottawa FLOAT,toronto_west_region FLOAT,toronto_east_region FLOAT,windsor FLOAT,London FLOAT,peterborough_city FLOAT,st_catharines FLOAT,sudbury FLOAT,sault_saint_marie FLOAT,thunder_bay FLOAT,north_bay FLOAT,timmins FLOAT,kenora FLOAT,parry_sound FLOAT,ontario_avg FLOAT,southern_avg FLOAT,northern_avg FLOAT,fuel_type VARCHAR,type_de_carburant VARCHAR);
GRANT SELECT ON ontario_fuel_prices TO pg;
