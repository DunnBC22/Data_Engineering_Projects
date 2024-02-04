select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select sales_year
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_3"
where sales_year is null



      
    ) dbt_internal_test