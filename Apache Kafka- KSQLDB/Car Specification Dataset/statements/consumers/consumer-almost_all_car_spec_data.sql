CREATE STREAM ALMOST_ALL_CAR_SPEC_DATA AS 
    SELECT 
        id,
        model,
        serie,
        company,
        body_style,
        segment,
        cylinders,
        displacement,
        power_hp,
        power_bhp,
        torque_lb_ft,
        electrical_motor_power,
        electrical_motor_torque,
        fuel_system,
        fuel,
        fuel_capacity,
        top_speed,
        acceleration_0_62,
        drive_type,
        gearbox,
        front_brake,
        rear_brake,
        tire_size,
        car_length,
        car_width,
        car_height,
        front_rear_track,
        wheelbase,
        ground_clearance,
        aerodynamics_cd,
        aerodynamics_frontal_area,
        turning_circle,
        cargo_volume,
        gross_weight_limit,
        combined_mpg,
        city_mpg,
        highway_mpg,
        co2_emissions,
        co2_emissions_combined,
        turning_circle_curb_to_curb,
        total_max_power,
        top_speed_electrical,
        total_max_torque,
        max_capacity
    FROM
        car_specs
    EMIT CHANGES;