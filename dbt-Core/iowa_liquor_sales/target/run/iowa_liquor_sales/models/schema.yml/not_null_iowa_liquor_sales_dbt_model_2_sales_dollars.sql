select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select sales_dollars
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_2"
where sales_dollars is null



      
    ) dbt_internal_test