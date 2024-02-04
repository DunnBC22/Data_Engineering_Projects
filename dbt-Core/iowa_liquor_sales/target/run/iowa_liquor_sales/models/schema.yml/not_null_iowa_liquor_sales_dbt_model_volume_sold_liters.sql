select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select volume_sold_liters
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model"
where volume_sold_liters is null



      
    ) dbt_internal_test