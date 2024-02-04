/*
    Title: Iowa Liquor Sales Pipeline

    Author: Brian Dunn

    Date: 01/26/2024

    Summary: Retrieve table and prepare it for analysis.

    Data Source: https://www.kaggle.com/datasets/prattayds/iowa-liquor-sales-full-dataset
*/

{{ config(materialized='view') }}

with source_data as (
    SELECT 
        ROW_NUMBER() OVER () as id,
        invoice_item_number,
        date_of_sale,
        CAST(COALESCE(EXTRACT(YEAR FROM date_of_sale), -1) AS INTEGER) AS sales_year,
        CAST(COALESCE(EXTRACT(MONTH FROM date_of_sale), -1) AS INTEGER) AS sales_month,
        CAST(COALESCE(EXTRACT(DAY FROM date_of_sale), -1) AS INTEGER) AS sales_day,
        store_number,
        TRIM(BOTH ' ' FROM store_name) AS store_name,
        TRIM(BOTH ' ' FROM store_address) AS store_address,
        TRIM(BOTH ' ' FROM store_city) AS store_city,
        CASE
            WHEN store_number = '4307' THEN '51529'
            ELSE COALESCE(REGEXP_REPLACE(store_zip_code, '[,"]', '', 'g'), '00000')
        END AS store_zip_code,
        store_location,
        store_county_number,
        TRIM(BOTH ' ' FROM store_county) AS store_county,
        TRIM(BOTH ' ' FROM item_category) AS item_category,
        TRIM(BOTH ' ' FROM category_name) AS category_name,
        vendor_number,
        TRIM(BOTH ' ' FROM vendor_name) AS vendor_name,
        item_number,
        item_description,
        COALESCE(pack, -1) AS pack,
        CAST(COALESCE(REGEXP_REPLACE(bottle_volume, '[,"]', '', 'g'), '-1') AS INTEGER) AS bottle_volume,
        CAST(COALESCE(REGEXP_REPLACE(state_bottle_cost, '[,"]', '', 'g'), '-1') AS FLOAT) AS state_bottle_cost,
        CAST(COALESCE(REGEXP_REPLACE(state_bottle_retail, '[,"]', '', 'g'), '-1') AS FLOAT) AS state_bottle_retail,
        CAST(COALESCE(REGEXP_REPLACE(bottles_sold, '[,"]', '', 'g'), '-1') AS INTEGER) AS bottles_sold,
        CAST(COALESCE(REGEXP_REPLACE(sale_dollars, '[,"]', '', 'g'), '-1') AS FLOAT) AS sales_dollars,
        CAST(COALESCE(REGEXP_REPLACE(volume_sold_liters, '[,"]', '', 'g'), '-1') AS FLOAT) AS volume_sold_liters,
        CAST(COALESCE(REGEXP_REPLACE(volume_sold_gallons, '[,"]', '', 'g'), '-1') AS FLOAT) AS volume_sold_gallons,
        CAST(COALESCE(REGEXP_REPLACE(iowa_zip_code_tabulation_areas, '[,"]', '', 'g'), '-1') AS FLOAT) AS iowa_zipcode_tab_areas,
        CAST(COALESCE(REGEXP_REPLACE(iowa_watershed_sub_basins, '[,"]', '', 'g'), '-1') AS FLOAT) AS iowa_watershed_sub_basins,
        CAST(COALESCE(REGEXP_REPLACE(iowa_watersheds, '[,"]', '', 'g'), '-1') AS FLOAT) AS iowa_watersheds,
        CAST(COALESCE(county_boundaries_of_iowa, '-1') AS FLOAT) AS iowa_county_boundaries,
        CAST(COALESCE(REGEXP_REPLACE(us_counties, '[,"]', '', 'g'), '-1') AS INTEGER) AS us_counties
    FROM iowa_liquor_sales
)
select
    id,
    store_number,
    store_name,
    store_city,
    store_zip_code,
    store_county,
    item_category,
    category_name,
    vendor_name,
    pack,
    bottle_volume,
    state_bottle_cost,
    state_bottle_retail,
    bottles_sold,
    sales_dollars,
    volume_sold_gallons,
    iowa_zipcode_tab_areas,
    iowa_watershed_sub_basins,
    iowa_watersheds,
    iowa_county_boundaries,
    us_counties,
    sales_year,
    sales_month,
    sales_day
from source_data