CREATE TABLE CAR_SPECS_HISTOGRAM AS 
    SELECT
        company AS Manufacturer,
        HISTOGRAM(model) AS Number_of_Each_Model,
        HISTOGRAM(serie) AS Number_of_Each_Series,
        HISTOGRAM(body_style) AS Number_of_Each_Body_Style,
        HISTOGRAM(segment) AS Number_of_Each_Segment,
        HISTOGRAM(cylinders) AS Number_of_Each_Cylinders,
        HISTOGRAM(fuel_system) AS Number_of_Each_Fuel_System,
        HISTOGRAM(fuel) AS Number_of_Each_Fuel,
        HISTOGRAM(drive_type) AS Number_of_Each_Drive_Type,
        HISTOGRAM(gearbox) AS Number_of_Each_Gearbox,
        HISTOGRAM(turning_circle) AS Number_of_Each_Turning_Circle,
        HISTOGRAM(cargo_volume) AS Number_of_Each_Cargo_Volume
    FROM
        car_specs
    GROUP BY
        company
    EMIT CHANGES;