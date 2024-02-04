{% snapshot iowa_liquor_sales_snapshot %}

{{
    config(
      target_database='dbt_ils',
      target_schema='snapshots',
      unique_key='id',

      strategy='check',
      check_cols='all'
    )
}}

select * from {{ ref('iowa_liquor_sales_dbt_model_3') }}

{% endsnapshot %}