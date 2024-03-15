CREATE STREAM stream_ontario_fuel_prices_1995_2005 AS 
    SELECT
        id,
        gas_price_date,
        SUBSTRING(gas_price_date, 1, 4) AS Gas_Price_Year,
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
    WHERE
        SUBSTRING(gas_price_date, 1, 4) IN (
            1995, 
            1996, 
            1997, 
            1998, 
            1999, 
            2000, 
            2001, 
            2002, 
            2003, 
            2004, 
            2005
            )
    EMIT CHANGES;