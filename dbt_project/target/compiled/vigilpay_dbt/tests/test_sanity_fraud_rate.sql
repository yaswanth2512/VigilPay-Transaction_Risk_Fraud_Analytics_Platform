-- Sanity bound test: Fails if overall fraud rate exceeds 5.0%
WITH overall_metrics AS (
    SELECT
        COUNT(*) AS total_txns,
        SUM(is_fraud) AS total_fraud,
        (100.0 * SUM(is_fraud) / COUNT(*)) AS overall_fraud_rate_pct
    FROM "paysim_ingestion"."main"."mart_transaction_summary"
)

SELECT *
FROM overall_metrics
WHERE overall_fraud_rate_pct > 5.0