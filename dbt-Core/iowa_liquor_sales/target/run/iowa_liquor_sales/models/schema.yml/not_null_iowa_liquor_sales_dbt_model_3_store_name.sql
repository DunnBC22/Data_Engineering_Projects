select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select store_name
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_3"
where store_name is null



      
    ) dbt_internal_test