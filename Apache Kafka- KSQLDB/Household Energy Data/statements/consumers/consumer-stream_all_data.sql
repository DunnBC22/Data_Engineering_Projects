CREATE STREAM STREAM_ALL_HOUSEHOLD_ENERGY_DATA AS
    SELECT
        energy_type,
        energy_date,
        start_time,
        end_time,
        energy_usage,
        energy_units,
        energy_cost,
        notes
    FROM
        household_energy_data
    EMIT CHANGES;