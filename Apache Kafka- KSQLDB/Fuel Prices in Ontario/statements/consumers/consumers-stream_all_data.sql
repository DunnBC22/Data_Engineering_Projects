CREATE STREAM STREAM_ALL_ONTARIO_FUEL_PRICES AS 
    SELECT
        id,
        gas_price_date,
        ottawa,
        toronto_west_region,
        toronto_east_region,
        windsor,
        london,
        peterborough_city,
        st_catharines,
        sudbury,
        sault_saint_marie,
        thunder_bay,
        north_bay,
        timmins,
        kenora,
        parry_sound,
        ontario_avg,
        southern_avg,
        northern_avg,
        fuel_type,
        type_de_carburant
    FROM
        ontario_fuel_prices
    EMIT CHANGES;