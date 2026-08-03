
  
  create view "paysim_ingestion"."main"."stg_transactions__dbt_tmp" as (
    WITH raw_source AS (
    SELECT * FROM vigilpay_raw.raw_transactions
),

cleaned AS (
    SELECT
        COALESCE(CAST(transaction_id AS VARCHAR), 'TXN_' || CAST(ROW_NUMBER() OVER () AS VARCHAR)) AS transaction_id,
        CAST(step AS INTEGER) AS step,
        UPPER(TRIM(CAST(type AS VARCHAR))) AS transaction_type,
        CAST(amount AS DOUBLE) AS amount,
        TRIM(CAST(name_orig AS VARCHAR)) AS user_id,
        CAST(oldbalance_org AS DOUBLE) AS old_balance_orig,
        CAST(newbalance_orig AS DOUBLE) AS new_balance_orig,
        TRIM(CAST(name_dest AS VARCHAR)) AS dest_id,
        CAST(oldbalance_dest AS DOUBLE) AS old_balance_dest,
        CAST(newbalance_dest AS DOUBLE) AS new_balance_dest,
        CAST(is_fraud AS INTEGER) AS is_fraud,
        CAST(is_flagged_fraud AS INTEGER) AS is_flagged_fraud,
        COALESCE(CAST(device_id AS VARCHAR), 'UNKNOWN') AS device_id,
        CAST(txn_timestamp AS VARCHAR) AS txn_timestamp,
        CAST(txn_date AS VARCHAR) AS txn_date,
        CAST(hour_of_day AS INTEGER) AS hour_of_day,
        CAST(load_timestamp AS VARCHAR) AS load_timestamp
    FROM raw_source
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY load_timestamp DESC) as row_num
    FROM cleaned
)

SELECT
    transaction_id,
    step,
    transaction_type,
    amount,
    user_id,
    old_balance_orig,
    new_balance_orig,
    dest_id,
    old_balance_dest,
    new_balance_dest,
    is_fraud,
    is_flagged_fraud,
    device_id,
    txn_timestamp,
    txn_date,
    hour_of_day,
    load_timestamp
FROM deduplicated
WHERE row_num = 1
  );
