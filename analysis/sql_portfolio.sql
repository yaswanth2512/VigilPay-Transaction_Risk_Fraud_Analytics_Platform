-- =============================================================================
-- VigilPay — SQL Analytics Query Portfolio (5 Production Analyst Queries)
-- Executed against mart_transaction_summary in DuckDB / BigQuery
-- =============================================================================

-- Q1: Fraud Rate & Total Volume by Transaction Type
SELECT
    transaction_type,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(amount), 2) AS total_volume,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3) AS fraud_rate_pct
FROM mart_transaction_summary
GROUP BY transaction_type
ORDER BY fraud_rate_pct DESC;


-- Q2: Fraud Trend Over Time (7-Day Moving Average via Window Function)
SELECT
    txn_date,
    COUNT(*) AS daily_txns,
    SUM(is_fraud) AS daily_fraud,
    ROUND(AVG(SUM(is_fraud)) OVER (
        ORDER BY txn_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS fraud_7day_moving_avg
FROM mart_transaction_summary
GROUP BY txn_date
ORDER BY txn_date;


-- Q3: Top 20 Riskiest Customers (CTE + Window Ranking)
WITH user_risk AS (
    SELECT
        user_id,
        COUNT(*) AS total_txns,
        SUM(is_fraud) AS fraud_txns,
        ROUND(AVG(amount), 2) AS avg_amount,
        ROUND(SUM(amount), 2) AS total_amount,
        ROUND(AVG(amount_to_avg_ratio), 2) AS avg_risk_multiplier,
        SUM(flag_10x_amount + flag_unseen_device + flag_unusual_hour) AS total_rule_flags
    FROM mart_transaction_summary
    GROUP BY user_id
)
SELECT
    user_id,
    total_txns,
    fraud_txns,
    avg_amount,
    total_amount,
    avg_risk_multiplier,
    total_rule_flags,
    DENSE_RANK() OVER (ORDER BY total_rule_flags DESC, avg_risk_multiplier DESC) AS risk_rank
FROM user_risk
ORDER BY risk_rank ASC
LIMIT 20;


-- Q4: Fraud Rate by Hour of Day (Peak Risk Window Detection)
SELECT
    hour_of_day,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3) AS fraud_rate_pct
FROM mart_transaction_summary
GROUP BY hour_of_day
ORDER BY fraud_rate_pct DESC;


-- Q5: Rule Contribution Precision & Coverage Analysis
WITH rule_triggers AS (
    SELECT '10x Amount Baseline' AS rule_name, flag_10x_amount AS triggered, is_fraud FROM mart_transaction_summary
    UNION ALL
    SELECT 'Unseen Device' AS rule_name, flag_unseen_device AS triggered, is_fraud FROM mart_transaction_summary
    UNION ALL
    SELECT 'Unusual Transaction Hour' AS rule_name, flag_unusual_hour AS triggered, is_fraud FROM mart_transaction_summary
)
SELECT
    rule_name,
    SUM(triggered) AS times_triggered,
    SUM(CASE WHEN triggered = 1 AND is_fraud = 1 THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN triggered = 1 AND is_fraud = 0 THEN 1 ELSE 0 END) AS false_positives,
    ROUND(100.0 * SUM(CASE WHEN triggered = 1 AND is_fraud = 1 THEN 1 ELSE 0 END) / NULLIF(SUM(triggered), 0), 2) AS precision_pct
FROM rule_triggers
GROUP BY rule_name
ORDER BY true_positives DESC;
