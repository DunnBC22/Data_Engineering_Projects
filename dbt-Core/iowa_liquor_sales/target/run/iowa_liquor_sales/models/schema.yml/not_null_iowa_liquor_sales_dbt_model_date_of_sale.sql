select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select date_of_sale
from "dbt_ils"."public"."iowa_liquor_sales_dbt_model"
where date_of_sale is null



      
    ) dbt_internal_test