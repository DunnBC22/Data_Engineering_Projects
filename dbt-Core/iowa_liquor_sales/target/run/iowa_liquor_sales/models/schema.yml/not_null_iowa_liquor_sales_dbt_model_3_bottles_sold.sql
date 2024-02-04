select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select bottles_sold
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_3"
where bottles_sold is null



      
    ) dbt_internal_test