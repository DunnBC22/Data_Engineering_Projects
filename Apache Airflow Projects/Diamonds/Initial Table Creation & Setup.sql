-- database name: diamonds_db
-- owner: airflow

CREATE TABLE diamonds (
    carat FLOAT,
    cut VARCHAR,
    color VARCHAR,
    clarity VARCHAR,
    diamond_depth FLOAT,
    table_value FLOAT,
    price INTEGER,
    x FLOAT,
    y FLOAT,
    z FLOAT
);

COPY diamonds(
    carat,
    cut,
    color,
    clarity,
    diamond_depth,
    table_value,
    price,
    x,
    y,
    z
    )
FROM '/Users/briandunn/Desktop/Projects 2/Diamonds/diamonds.csv'
DELIMITER ','
CSV HEADER;