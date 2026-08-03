WITH stg_txns AS (
    SELECT * FROM "paysim_ingestion"."main"."stg_transactions"
),

user_baselines AS (
    SELECT
        user_id,
        AVG(amount) AS user_avg_amount,
        STDDEV(amount) AS user_std_amount,
        MAX(amount) AS user_max_amount,
        COUNT(*) AS user_total_txns,
        MODE(device_id) AS user_primary_device,
        MODE(hour_of_day) AS user_usual_hour
    FROM stg_txns
    GROUP BY user_id
)

SELECT
    user_id,
    ROUND(user_avg_amount, 2) AS user_avg_amount,
    COALESCE(ROUND(user_std_amount, 2), 0.0) AS user_std_amount,
    ROUND(user_max_amount, 2) AS user_max_amount,
    user_total_txns,
    user_primary_device,
    user_usual_hour
FROM user_baselines