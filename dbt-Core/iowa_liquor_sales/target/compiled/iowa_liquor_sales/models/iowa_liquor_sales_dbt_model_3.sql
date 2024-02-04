/*
    Title: Iowa Liquor Sales Pipeline

    Author: Brian Dunn

    Date: 01/26/2024

    Summary: Retrieve table and prepare it for analysis.

    Data Source: https://www.kaggle.com/datasets/prattayds/iowa-liquor-sales-full-dataset
*/



WITH filtered_data AS (
    SELECT *
    FROM "dbt_ils"."public"."iowa_liquor_sales_dbt_model_2"
    WHERE sales_dollars < 10001
)

SELECT *
FROM filtered_data