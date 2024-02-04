
  
    

  create  table "dbt_ils"."public"."iowa_liquor_sales_dbt_model_2__dbt_tmp"
  
  
    as
  
  (
    /*
    Title: Iowa Liquor Sales Pipeline

    Author: Brian Dunn

    Date: 01/26/2024

    Summary: Retrieve table and prepare it for analysis.

    Data Source: https://www.kaggle.com/datasets/prattayds/iowa-liquor-sales-full-dataset
*/



with cleaned_data as (
    select
        *
    from "dbt_ils"."public"."iowa_liquor_sales_dbt_model"
    where
        (
            
                store_number is not null
                 and 
            
                store_name is not null
                 and 
            
                store_city is not null
                 and 
            
                store_zip_code is not null
                 and 
            
                store_county is not null
                 and 
            
                item_category is not null
                 and 
            
                category_name is not null
                 and 
            
                vendor_name is not null
                 and 
            
                state_bottle_cost is not null
                 and 
            
                state_bottle_retail is not null
                 and 
            
                sales_dollars is not null
                 and 
            
                iowa_zipcode_tab_areas is not null
                 and 
            
                iowa_watershed_sub_basins is not null
                 and 
            
                iowa_watersheds is not null
                 and 
            
                iowa_county_boundaries is not null
                 and 
            
                us_counties is not null
                
            
        )
)

select * from cleaned_data
  );
  