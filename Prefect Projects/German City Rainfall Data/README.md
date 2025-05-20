# German City Rainfall Data - Prefect Pipeline


## Notes

- These are the transformations I applied to this dataset:
    - Rename features
        - "City": "RecordedCity",
        - "Latitude": "RecordedLatitude",
        - "Longitude": "RecordedLongitude",
        - "Month": "RecordedMonth",
        - "Year": "RecordedYear",
        - "Rainfall (mm)": "RainfallInMillimeters",
        - "Elevation (m)": "ElevationInMeters",
        - "Climate_Type": "ClimateType",
        - "Temperature (°C)": "TemperatureInCelsius",
        - "Humidity (%)": "HumidityPercent"
    - Clean Values:
        - Remove leading and trailing whitespace for values in these features:
            - RecordedCity
            - ClimateType
    - Handle Geographical data:
        - Create new Geo POINT feature using the RecordedLatitude & RecordedLongitude Features
    - Remove features
        - RecordedLatitude (after creating new Geo POINT feature)
        - RecordedLongitude (after creating new Geo POINT feature)


## Dataset Source
https://www.kaggle.com/datasets/heidarmirhajisadati/germany-city-rainfall-data