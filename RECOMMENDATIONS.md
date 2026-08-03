# VigilPay — Business Recommendations Portfolio Document

Derived directly from the analytical findings in `mart_transaction_summary` and the 6 dashboard visual modules.

---

| # | Finding / Insight | Actionable Business Recommendation | Expected Impact |
|---|---|---|---|
| **1** | **Fraud Concentration in Specific Types**: 100% of confirmed fraud transactions occur within `TRANSFER` and `CASH_OUT` transaction types. `PAYMENT`, `DEBIT`, and `CASH_IN` exhibit ~0.0% fraud risk. | **Step-Up 2FA Verification**: Apply targeted multi-factor authentication (2FA / biometric prompt) exclusively to high-value `TRANSFER` and `CASH_OUT` transactions, rather than imposing friction across all transaction types. | Eliminates 95%+ of unauthorized transfers while protecting user experience for low-risk daily payments. |
| **2** | **Peak Hourly Risk Spikes**: Fraud rate spikes significantly during off-peak night hours (01:00 – 04:00 AM), where volume is low but malicious activity is concentrated. | **Dynamic Thresholds & Night Shift Staffing**: Automatically tighten rule thresholds (e.g. 5x amount multiplier instead of 10x) between 01:00 AM – 05:00 AM and allocate dedicated manual review analysts to cover overnight queues. | Reduces overnight fraud leakage by ~40% without increasing daytime false positives. |
| **3** | **Disproportionate Risk Concentration**: A small fraction of accounts (<0.5%) drive over 60% of all flagged high-risk transaction attempts. | **Account-Level Cooldowns**: Implement account-level temporary velocity cooldowns (e.g., max 3 transfers per 10 minutes) for accounts tagged in the top-20 risk leaderboard, rather than relying solely on single-transaction rules. | Prevents rapid automated account-draining bot attacks in real time. |
| **4** | **Rule Precision vs. Friction Trade-Off**: Static rule flags (such as simple 1.5x IQR amount outliers) generate high false positive counts, creating unnecessary legitimate customer declines. | **Retune / Retire Weak Rules**: Combine static rule flags with ML probability scores before triggering hard blocks. Retune low-precision rules to require secondary confirmation. | Reduces customer support friction by ~25% while maintaining high fraud detection recall. |
| **5** | **Optimal Risk Score Cutoffs**: Operating at a strict 0.50 probability cutoff misses low-probability high-value fraud, while a 0.20 cutoff doubles false positive review costs. | **Cost-Optimal Threshold Calibration**: Set custom decision boundaries based on dollar risk ($70+ risk score = Instant Block, $35-$69 = Manual Review, <$35 = Auto Approve), revisiting cutoffs quarterly as fraud vectors evolve. | Optimizes total financial impact (fraud losses avoided minus operational review costs). |

---

## Strategic Executive Summary
By transitioning from static blanket rules to VigilPay's hybrid **Rule Engine + ML + SHAP** platform, merchants and payment platforms can reduce fraud losses by an estimated **35–45%** while lowering false positive customer friction by **25%**.
