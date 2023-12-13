-- database owner: ippp_db
-- owner: airflow

CREATE TABLE insur_prod_pur_pred (
    customer_ID INTEGER,
    shopping_pt INTEGER,
    record_type INTEGER,
    day_of_week INTEGER,
    time_of_day TIME,
    state_where_sale VARCHAR,
    location_ID INTEGER,
    group_size INTEGER,
    homeowner INTEGER,
    car_age INTEGER,
    car_value VARCHAR,
    risk_factor VARCHAR,
    age_oldest INTEGER,
    age_youngest INTEGER,
    married_couple INTEGER,
    C_previous VARCHAR,
    duration_previous VARCHAR,
    A INTEGER,
    B INTEGER,
    C INTEGER,
    D INTEGER,
    E INTEGER,
    F INTEGER,
    G INTEGER,
    cost INTEGER
);

COPY insur_prod_pur_pred(
    customer_ID,
    shopping_pt,
    record_type,
    day_of_week,
    time_of_day,
    state_where_sale,
    location_ID,
    group_size,
    homeowner,
    car_age,
    car_value,
    risk_factor,
    age_oldest,
    age_youngest,
    married_couple,
    C_previous,
    duration_previous,
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    cost
    )
FROM '/Users/briandunn/Desktop/Projects 2/Insurance Product Purchase Prediction/train.csv'
DELIMITER ','
CSV HEADER;