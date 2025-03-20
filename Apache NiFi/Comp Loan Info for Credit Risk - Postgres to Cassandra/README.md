# Comp Loan Info For Credit Risk - Apache NiFi Pipeline

This project retrieves data from a Postgres table, makes transformations and then sends them to an Apaceh Cassandra table. Apache NiFi, Postgres, and Apache Cassandra are all in their own docker containers.

I have included the Flow Definition Files (both with and without exernal services).

## Notes

- There is one feature that is a single value column (just remove this feature): application_type. 
- The only feature with missing values is: emp_title. To handle these, I am going to impute the missing values with 'No Employee Title Listed'.
- I converted these categorical columns from string values to numerical (integer) values according to these charts:
    - term
        - ' 36 months' -> 0
        - ' 60 months' -> 1
    - purpose
        - car -> 0
        - credit card -> 1
        - Debt consolidation -> 2
        - educational -> 3
        - home improvement -> 4
        - house -> 5
        - major purchase -> 6
        - medical -> 7
        - moving -> 8
        - other -> 9
        - renewable_energy -> 10
        - small business -> 11
        - vacation -> 12
        - wedding -> 13
    - verification_status
        - Source Verified   -> 0
        - Verified   -> 1
        - Not Verified   -> 2
    - home_ownership
        - RENT  ->  0
        - MORTGAGE  ->  1
        - OWN  ->  2
        - OTHER  -> 3
        - NONE  ->  4
    - loan_status
        - Fully Paid -> 0
        - Current -> 1
        - Charged Off -> 2
- Remove leading & trailing whitespace from these columns:
    - address_state
    - emp_title
    - grade
    - sub_grade
- Handle dates, times, & timestamps:
    - issue_date,
    - last_credit_pull_date,
    - last_payment_date,
    - next_payment_date,
- emp_length: remove the year or years from the end of the string and rename to emp_length_years (also trim leading and trailing whitespace)

## Dataset Source
https://www.kaggle.com/datasets/nezukokamaado/auto-loan-dataset