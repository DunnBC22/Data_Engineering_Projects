# RHMCD 20 - Apache Nifi Pipeline

This project retrieves data from a table in MySQL, makes transformations and then sends it to a table in Apache Cassandra. Apache NiFi, MySQL, and Apache Cassandra are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).


## Notes

- There are no missing values.
- I made sure to convert Categorical String values with integer values. Here are the conversions:
    - age: 
        - '16-20'   ->  0
        - '20-25'   ->  1
        - '25-30'   ->  2
        - '30-Above'   ->  3
    - sex:
        - 'Male'    ->  0
        - 'Female'    ->  1
    - occupation:
        - 'Business'   ->  0
        - 'Corporate'   ->  1
        - 'Housewife'   ->  2
        - 'Others'   ->  3
        - 'Student'   ->  4
    - days_indoors:
        - 'More than 2 months'   ->  0
        - '31-60 days'   ->  1
        - 'Go out Every day'   ->  2
        - '1-14 days'   ->  3
        - '15-30 days'   ->  4
    - growing_stress: 
        - 'No'   ->  0
        - 'Maybe'   ->  1
        - 'Yes'   ->   2
    - quarantine_frustrations:
        - 'No'   ->  0
        - 'Maybe'   ->  1
        - 'Yes'   ->   2
    - changes_habits:
        - 'No'   ->  0
        - 'Maybe'   ->  1
        - 'Yes'   ->  2
    - mental_health_history:
        - 'No'   ->  0
        - 'Maybe'   ->  1
        - 'Yes'   ->  2
    - weight_change: 
        - 'No'   ->  0
        - 'Maybe'   ->  1
        - 'Yes'   ->  2
    - mood_swings:
        - 'Low'    ->  0
        - 'Medium'   ->  1
        - 'High'   ->  2
    - coping_struggles: 
        - 'No'   ->  0
        - 'Yes'   ->  1
    - work_interest:
        - 'No'   ->  0
        - 'Maybe'   ->  1
        - 'Yes'   ->  2
    - social_weakness:
        - 'No\r'   ->  0
        - 'Maybe\r'   ->  1
        - 'Yes\r'   ->  2

## Dataset Source
https://www.kaggle.com/datasets/imtkaggleteam/rhmcd-20-depression