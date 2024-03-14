CREATE STREAM ACURA_CAR_SPECS AS 
    SELECT
        id AS record_id,
        model AS Model,
        serie AS Car_Series,
        company AS Manufacturer,
        body_style AS Body_Style,
        segment AS Vehicle_Segment,
        cylinders AS Number_of_Cylinders,
        fuel_system AS Vehicle_Fuel_System,
        fuel AS Fuel,
        drive_type AS Vehicle_Drive_Type,
        gearbox AS Gearbox,
        turning_circle AS Turning_Circle,
        cargo_volume AS Cargo_Volume
    FROM
        car_specs
    WHERE
        model LIKE '%ACURA%'
    OR 
        model LIKE '%Acura%'
    OR 
        model LIKE '%acura%'
    EMIT CHANGES;