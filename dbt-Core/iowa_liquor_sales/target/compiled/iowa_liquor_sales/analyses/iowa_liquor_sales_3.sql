WITH iowa_liquor_data as (
    SELECT 
        id,
        store_number,
        store_name,
        store_city,
        store_county,
        item_category,
        category_name,
        vendor_name,
        bottles_sold,
        sales_dollars,
        us_counties,
        sales_year,
        sales_month,
        sales_day
    FROM "dbt_ils"."public"."iowa_liquor_sales_dbt_model_3"
)

SELECT
    SUM(sales_dollars) OVER (PARTITION BY store_county ORDER BY id ROWS UNBOUNDED PRECEDING)
FROM iowa_liquor_data
ORDER BY store_county