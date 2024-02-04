/*
    Title: Iowa Liquor Sales Pipeline

    Author: Brian Dunn

    Date: 01/26/2024

    Summary: Retrieve table and prepare it for analysis.

    Data Source: https://www.kaggle.com/datasets/prattayds/iowa-liquor-sales-full-dataset
*/

{{ config(materialized='table') }}

with cleaned_data as (
    select
        *
    from {{ ref('iowa_liquor_sales_dbt_model') }}
    where
        (
            {% for column in [
                'store_number',
                'store_name',
                'store_city',
                'store_zip_code',
                'store_county',
                'item_category',
                'category_name',
                'vendor_name',
                'state_bottle_cost',
                'state_bottle_retail',
                'sales_dollars',
                'iowa_zipcode_tab_areas',
                'iowa_watershed_sub_basins',
                'iowa_watersheds',
                'iowa_county_boundaries',
                'us_counties'] 
                              %}
                {{ column }} is not null
                {% if not loop.last %} and {% endif %}
            {% endfor %}
        )
)

select * from cleaned_data
