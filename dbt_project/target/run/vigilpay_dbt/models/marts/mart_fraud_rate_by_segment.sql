
  
    
    

    create  table
      "paysim_ingestion"."main"."mart_fraud_rate_by_segment__dbt_tmp"
  
    as (
      WITH summary AS (
    SELECT * FROM "paysim_ingestion"."main"."mart_transaction_summary"
),

segmented AS (
    SELECT
        transaction_type,
        hour_of_day,
        COUNT(*) AS total_transactions,
        SUM(is_fraud) AS fraud_transactions,
        SUM(amount) AS total_amount,
        SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) AS fraud_amount,
        ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3) AS fraud_rate_pct
    FROM summary
    GROUP BY transaction_type, hour_of_day
)

SELECT * FROM segmented
    );
  
  