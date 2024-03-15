CREATE STREAM household_energy_data (
    energy_type VARCHAR,
    energy_date VARCHAR,
    start_time VARCHAR,
    end_time VARCHAR,
    energy_usage DOUBLE,
    energy_units VARCHAR,
    energy_cost VARCHAR,
    notes VARCHAR
    )
    WITH (
        kafka_topic='household_energy',
        value_format='json', 
        partitions=4
    );
