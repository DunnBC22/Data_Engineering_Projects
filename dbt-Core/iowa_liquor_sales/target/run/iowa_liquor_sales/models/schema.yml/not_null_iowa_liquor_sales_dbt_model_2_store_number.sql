select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select store_number
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_2"
where store_number is null



      
    ) dbt_internal_test