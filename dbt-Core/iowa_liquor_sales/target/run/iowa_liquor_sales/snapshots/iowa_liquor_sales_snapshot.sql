
      
  
    

  create  table "dbt_ils"."snapshots"."iowa_liquor_sales_snapshot"
  
  
    as
  
  (
    

    select *,
        md5(coalesce(cast(id as varchar ), '')
         || '|' || coalesce(cast(now()::timestamp without time zone as varchar ), '')
        ) as dbt_scd_id,
        now()::timestamp without time zone as dbt_updated_at,
        now()::timestamp without time zone as dbt_valid_from,
        nullif(now()::timestamp without time zone, now()::timestamp without time zone) as dbt_valid_to
    from (
        



select * from "dbt_ils"."public"."iowa_liquor_sales_dbt_model_3"

    ) sbq



  );
  
  