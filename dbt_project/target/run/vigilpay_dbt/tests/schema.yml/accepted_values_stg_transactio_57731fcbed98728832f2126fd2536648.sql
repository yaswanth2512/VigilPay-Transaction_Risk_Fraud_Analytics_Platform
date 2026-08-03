
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        transaction_type as value_field,
        count(*) as n_records

    from "paysim_ingestion"."main"."stg_transactions"
    group by transaction_type

)

select *
from all_values
where value_field not in (
    'PAYMENT','TRANSFER','CASH_OUT','CASH_IN','DEBIT'
)



  
  
      
    ) dbt_internal_test