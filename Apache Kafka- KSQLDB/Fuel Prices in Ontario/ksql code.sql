-- Create stream: ontario_fuel_prices
CREATE STREAM ontario_fuel_prices (
    _id INTEGER,
    gas_price_date TIMESTAMP,
    ottawa DOUBLE,
    toronto_west_region DOUBLE,
    toronto_east_region DOUBLE,
    windsor DOUBLE,
    London DOUBLE,
    peterborough_city DOUBLE,
    st_catharines DOUBLE,
    sudbury DOUBLE,
    sault_saint_marie DOUBLE,
    thunder_bay DOUBLE,
    north_bay DOUBLE,
    timmins DOUBLE,
    kenora DOUBLE,
    parry_sound DOUBLE,
    ontario_avg DOUBLE,
    southern_avg DOUBLE,
    northern_avg DOUBLE,
    fuel_type VARCHAR,
    type_de_carburant VARCHAR
) 
WITH 
(
    kafka_topic='ontario_fuel_prices',
    value_format='json', 
    partitions=1
);