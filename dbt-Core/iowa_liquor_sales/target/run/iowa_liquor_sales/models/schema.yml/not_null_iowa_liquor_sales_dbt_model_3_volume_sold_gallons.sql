select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select volume_sold_gallons
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_3"
where volume_sold_gallons is null



      
    ) dbt_internal_test