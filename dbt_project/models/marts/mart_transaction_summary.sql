WITH txns AS (
    SELECT * FROM {{ ref('stg_transactions') }}
),

baselines AS (
    SELECT * FROM {{ ref('int_user_behavior_baseline') }}
),

joined AS (
    SELECT
        t.transaction_id,
        t.step,
        t.txn_timestamp,
        t.txn_date,
        t.hour_of_day,
        t.transaction_type,
        t.amount,
        t.user_id,
        t.dest_id,
        t.device_id,
        t.old_balance_orig,
        t.new_balance_orig,
        t.old_balance_dest,
        t.new_balance_dest,
        t.is_fraud,
        t.is_flagged_fraud,
        
        -- User baseline metrics
        b.user_avg_amount,
        b.user_primary_device,
        b.user_usual_hour,
        b.user_total_txns,
        
        -- Engineered feature ratios & deltas
        ROUND(t.amount / NULLIF(b.user_avg_amount, 0), 2) AS amount_to_avg_ratio,
        CASE WHEN t.device_id != b.user_primary_device THEN 1 ELSE 0 END AS is_new_device,
        ABS(t.hour_of_day - COALESCE(b.user_usual_hour, t.hour_of_day)) AS hour_diff,
        ROUND(t.old_balance_orig - t.new_balance_orig, 2) AS balance_delta_orig,
        ROUND(t.new_balance_dest - t.old_balance_dest, 2) AS balance_delta_dest,

        -- Rule Trigger Flags
        CASE WHEN t.amount > (10 * COALESCE(b.user_avg_amount, 1000)) THEN 1 ELSE 0 END AS flag_10x_amount,
        CASE WHEN t.device_id != b.user_primary_device THEN 1 ELSE 0 END AS flag_unseen_device,
        CASE WHEN ABS(t.hour_of_day - COALESCE(b.user_usual_hour, t.hour_of_day)) > 4 THEN 1 ELSE 0 END AS flag_unusual_hour
    FROM txns t
    LEFT JOIN baselines b ON t.user_id = b.user_id
)

SELECT * FROM joined
