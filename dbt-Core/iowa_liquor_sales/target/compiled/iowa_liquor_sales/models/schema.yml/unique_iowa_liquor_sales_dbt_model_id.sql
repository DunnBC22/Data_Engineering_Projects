
    
    

select
    id as unique_field,
    count(*) as n_records

from "dbt_ils"."public"."iowa_liquor_sales_dbt_model"
where id is not null
group by id
having count(*) > 1


