# US Schools Dataset - Prefect Pipeline






## Notes

- Since there is an inconsistency in feature naming, make sure to correct these features names prior to joining the two datasets
    - ST_GRADE & START_GRAD are the same feature
    - DISTRICTID & FID are also the same feature
- Convert to Dates (without time) from string and extract date parts 
    - SOURCEDATE
    - VAL_DATE
- Handle Geographical data points
    - Combine LATITUDE & LONGITUDE to create the geographical points for each school
- Remove these columns
    - X (duplicative)
    - Y (duplicative)
    - NAICS_CODE (single value feature)
    - NAICS_DESC (single value feature)
    - OBJECTID (Remove, since I will provide a new one for the combination of both datasets)
- No Nulls to have to handle
- Rename Features as necessary
- Clean string values up by:
    - Remove leading and trailing whitespace
    - Title Case the values (to make them easier to read)
- Handle these Discrete-valued Features
    - STATE
    - COUNTRY
    - VAL_METHOD
    - LEVEL_
    - END_GRADE





STILL NEED TO IMPUTE/HANDLE MISSING VALUES:

in ValidationMethod:
VAL_METHOD (4)
['IMAGERY/OTHER' 'IMAGERY' 'UNVERIFIED' 'GEOCODE']
-> convert / to space THEN titlecase values THEN remove all whitespace



- If the values in these features are not numerical, replace the values with:
"DistrictPopulation": "-1"
"SchoolEnrollment": "-1"
"NumOfFullTimeTeachers": "-1"

## Dataset Source
