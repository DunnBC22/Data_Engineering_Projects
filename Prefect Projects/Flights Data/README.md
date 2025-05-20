# Flight Data - KNIME Pipeline



## Description

- These are the transformations that I applied to this dataset:
    - Rename features
        - "TRANSACTIONID": "TransactionId",
        - "FLIGHTDATE": "FlightDate",
        - "AIRLINECODE": "AirlineCode",
        - "TAILNUM": "TailNumber",
        - "FLIGHTNUM": "FlightNumber",
        - "ORIGINAIRPORTCODE": "OriginAirportCode",
        - "ORIGINCITYNAME": "OriginCityName",
        - "ORIGINSTATE": "OriginState",
        - "DESTAIRPORTCODE": "DestinationAirportCode",
        -"DESTCITYNAME": "DestinationCityName",
        - "DESTSTATE": "DestinationState",
        - "CRSDEPTIME": "CrsDepartureTime",
        - "DEPTIME": "DepartureTime",
        - "DEPDELAY": "DepartureDelay",
        - "TAXIOUT": "TaxiOut",
        - "WHEELSOFF": "WheelsOff",
        - "WHEELSON": "WheelsOn",
        - "TAXIIN": "TaxiIn",
        - "CRSARRTIME": "CrsArrivalTime",
        - "ARRTIME": "ArrivalTime",
        - "ARRDELAY": "ArrivalDelay",
        - "CRSELAPSEDTIME": "CrsElapsedTime",
        - "ACTUALELAPSEDTIME": "ActualElapsedTime",
        - "CANCELLED": "FlightCancelled",
        - "DIVERTED": "FlightDiverted",
        - "DISTANCE": "FlightDistance",
        - "ORIGAIRPORTNAME": "OriginAirportName",
        - "ORIGINSTATENAME": "OriginStateName",
        - "DESTAIRPORTNAME": "DestinationAirportName",
        - "DESTSTATENAME": "DestinationStateName"
    - Remove Features:
        - AIRLINENAME (duplicative)
        - ORIGAIRPORTNAME (duplicative)
        - ORIGINSTATENAME (duplicative)
        - DESTAIRPORTNAME (duplicative)
        - DESTSTATENAME (duplicative)
    - Handle/Impute Missing Values:
        - For the following features, remove the record if there is a null in any of the following features: 
            - OriginState
            - DestinationState
            - DepartureTime
            - DepartureDelay
            - ArrivalTime
            - ArrivalDelay
            - CrsElapsedTime
            - ActualElapsedTime
    - Impute these values for missing values in these features:
        - TailNumber -> "UNKNOWN"
        - TaxiOut -> -1000
        - WheelsOff -> -1000
        - WheelsOn -> -1000
        - TaxiIn -> -1000     
    - Clean values:
        - FlightCancelled: multiple values for true and false
        - FlightDiverted: multiple values for true and false
        - FlightDistance: remove the appended ' miles' from each feature
    - Remove leading and trailing whitespace from these features:
        - AirlineCode
        - TailNumber
        - OriginAirportCode
        - OriginCityName
        - OriginState
        - DestinationAirportCode
        - DestinationCityName
        - DestinationState
    - Convert data types to:
        - "FlightCancelled": "boolean"
        - "FlightDiverted": "boolean"
        - "FlightDistane": "int"
    - Handle date data & make sure to extract date parts:
        - FlightDate
    - for the airports table, make sure to clean up the airport names (remove everything from the ":" and to the right)
    - Create nodes table
    - Create relationships table


## Dataset Source
https://www.kaggle.com/datasets/mmetter/flights