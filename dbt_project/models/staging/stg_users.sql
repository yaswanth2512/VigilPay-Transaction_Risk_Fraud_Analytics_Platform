WITH transactions AS (
    SELECT * FROM {{ ref('stg_transactions') }}
),

user_summary AS (
    SELECT
        user_id,
        COUNT(*) AS total_transactions,
        MIN(txn_timestamp) AS first_transaction_at,
        MAX(txn_timestamp) AS last_transaction_at,
        AVG(amount) AS overall_avg_amount,
        MAX(amount) AS overall_max_amount,
        MODE(device_id) AS primary_device_id
    FROM transactions
    GROUP BY user_id
)

SELECT * FROM user_summary
