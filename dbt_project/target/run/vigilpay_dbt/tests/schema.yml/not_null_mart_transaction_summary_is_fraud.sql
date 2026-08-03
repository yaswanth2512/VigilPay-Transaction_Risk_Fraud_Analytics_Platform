
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select is_fraud
from "paysim_ingestion"."main"."mart_transaction_summary"
where is_fraud is null



  
  
      
    ) dbt_internal_test