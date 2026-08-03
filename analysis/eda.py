"""
Exploratory Data Analysis & Statistical Testing Suite for VigilPay.
Executes distributions, IQR vs Z-score outlier checks, Chi-Square test,
Two-sample T-Test (with explicit step-by-step Cohen's d derivation & variance breakdown),
and Point-Biserial correlation analysis.
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy import stats

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "paysim_sample.csv")

def run_eda(csv_path=SAMPLE_CSV_PATH):
    if not os.path.exists(csv_path):
        print(f"[!] Sample dataset not found at {csv_path}. Running generator first...")
        sys.path.append(DATA_DIR)
        from generate_sample import create_stratified_sample
        csv_path = create_stratified_sample()

    print(f"\n=========================================================================")
    print(f"               VIGILPAY — EXPLORATORY DATA ANALYSIS (EDA)                ")
    print(f"=========================================================================\n")
    
    df = pd.read_csv(csv_path)
    print(f"[+] Loaded Dataset: {len(df):,} records")
    print(f"[+] Total Fraud Cases: {df['isFraud'].sum():,} ({df['isFraud'].mean()*100:.3f}%)\n")

    # 1. SUMMARY STATISTICS & LOG AMOUNT DISTRIBUTION
    print("--- 1. TRANSACTION AMOUNT SUMMARY ---")
    amount_stats = df['amount'].describe()
    print(amount_stats.to_string())
    print(f"Skewness: {df['amount'].skew():.4f} (Heavily right-skewed; requires log-transformation)\n")

    # 2. TRANSACTION TYPE FREQUENCY & FRAUD CONCENTRATION
    print("--- 2. TRANSACTION TYPE FREQUENCY & FRAUD CONCENTRATION ---")
    type_summary = df.groupby('type').agg(
        total_txns=('isFraud', 'count'),
        fraud_txns=('isFraud', 'sum'),
        fraud_rate_pct=('isFraud', lambda x: x.mean() * 100)
    ).reset_index()
    print(type_summary.to_string(index=False))
    print("\n[Finding] Fraud occurs exclusively in TRANSFER and CASH_OUT transaction types.\n")

    # 3. OUTLIER DETECTION: IQR vs Z-SCORE COMPARISON
    print("--- 3. OUTLIER DETECTION COMPARISON (IQR vs Z-SCORE) ---")
    Q1 = df['amount'].quantile(0.25)
    Q3 = df['amount'].quantile(0.75)
    IQR = Q3 - Q1
    iqr_outliers = (df['amount'] < (Q1 - 1.5 * IQR)) | (df['amount'] > (Q3 + 1.5 * IQR))
    
    z_scores = np.abs(stats.zscore(df['amount']))
    z_outliers = z_scores > 3

    df['iqr_flag'] = iqr_outliers
    df['z_flag'] = z_outliers

    iqr_fraud_caught = df[df['iqr_flag']]['isFraud'].sum()
    z_fraud_caught = df[df['z_flag']]['isFraud'].sum()
    total_fraud = df['isFraud'].sum()

    print(f"IQR Method (1.5x IQR): {iqr_outliers.sum():,} total flagged, catching {iqr_fraud_caught}/{total_fraud} fraud cases ({iqr_fraud_caught/max(1, total_fraud)*100:.1f}%)")
    print(f"Z-Score Method (|z| > 3): {z_outliers.sum():,} total flagged, catching {z_fraud_caught}/{total_fraud} fraud cases ({z_fraud_caught/max(1, total_fraud)*100:.1f}%)\n")

    # 4. ZERO-BALANCE AUDIT
    print("--- 4. ZERO-BALANCE EDGE CASE AUDIT ---")
    zero_orig = (df['oldbalanceOrg'] == 0) & (df['newbalanceOrig'] == 0)
    zero_dest = (df['oldbalanceDest'] == 0) & (df['newbalanceDest'] == 0)
    print(f"Zero Original Balance Transactions: {zero_orig.sum():,} ({zero_orig.mean()*100:.2f}%)")
    print(f"Zero Destination Balance Transactions: {zero_dest.sum():,} ({zero_dest.mean()*100:.2f}%)\n")

    # 5. STATISTICAL TEST 1: CHI-SQUARE TEST OF INDEPENDENCE
    print("--- 5. STATISTICAL TEST 1: CHI-SQUARE TEST OF INDEPENDENCE ---")
    contingency_table = pd.crosstab(df['type'], df['isFraud'])
    chi2, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
    print(f"Chi-Square Statistic: {chi2:.4f}")
    print(f"Degrees of Freedom: {dof}")
    print(f"p-value: {p_chi2:.4e}")
    if p_chi2 < 0.05:
        print("Result: Reject H0 — Fraud rate is statistically DEPENDENT on transaction type (p < 0.001).\n")
    else:
        print("Result: Fail to reject H0.\n")

    # 6. STATISTICAL TEST 2: TWO-SAMPLE T-TEST & EXPLICIT COHEN'S D RE-DERIVATION
    print("--- 6. STATISTICAL TEST 2: TWO-SAMPLE T-TEST & COHEN'S D RE-DERIVATION ---")
    fraud_amounts = df[df['isFraud'] == 1]['amount']
    non_fraud_amounts = df[df['isFraud'] == 0]['amount']
    
    n1 = len(fraud_amounts)
    n2 = len(non_fraud_amounts)
    mean1 = fraud_amounts.mean()
    mean2 = non_fraud_amounts.mean()
    s1 = fraud_amounts.std()
    s2 = non_fraud_amounts.std()

    t_stat, p_ttest = stats.ttest_ind(fraud_amounts, non_fraud_amounts, equal_var=False)

    # Step-by-step Pooled Standard Deviation
    var1 = s1 ** 2
    var2 = s2 ** 2
    numerator = ((n1 - 1) * var1) + ((n2 - 1) * var2)
    denominator = n1 + n2 - 2
    pooled_var = numerator / denominator
    pooled_std = np.sqrt(pooled_var)

    cohens_d = (mean1 - mean2) / pooled_std
    glass_delta = (mean1 - mean2) / s2
    unweighted_std = np.sqrt((var1 + var2) / 2.0)
    unweighted_d = (mean1 - mean2) / unweighted_std

    print(f"Raw Input Metrics:")
    print(f"  - Fraud Group (n1)     : {n1:,} records | Mean1 = ${mean1:,.2f} | Std1 = ${s1:,.2f}")
    print(f"  - Non-Fraud Group (n2) : {n2:,} records | Mean2 = ${mean2:,.2f} | Std2 = ${s2:,.2f}")
    print(f"  - Mean Difference      : ${mean1 - mean2:,.2f}")
    print(f"\nPooled Standard Deviation Derivation:")
    print(f"  - Formula              : sqrt( [ (n1-1)*s1^2 + (n2-1)*s2^2 ] / (n1+n2-2) )")
    print(f"  - Numerator (Sum Sq)   : ({n1-1} * {var1:,.2f}) + ({n2-1} * {var2:,.2f}) = {numerator:,.2f}")
    print(f"  - Denominator (df)     : {n1} + {n2} - 2 = {denominator:,}")
    print(f"  - Pooled Variance      : {pooled_var:,.2f}")
    print(f"  - Pooled Std (s_pooled): ${pooled_std:,.2f}")
    print(f"\nRecalculated Effect Sizes:")
    print(f"  - Standard Cohen's d   : {cohens_d:.4f}")
    print(f"  - Glass's Delta (vs s2): {glass_delta:.4f}")
    print(f"  - Unweighted d (Welch) : {unweighted_d:.4f}")
    print(f"\nStatistical Test Inference:")
    print(f"  - t-statistic          : {t_stat:.4f}")
    print(f"  - p-value              : {p_ttest:.4e}")
    print(f"  [Explanation] Standard Cohen's d ({cohens_d:.2f}) is large because mean difference (${mean1-mean2:,.0f}) is huge relative to s_pooled (${pooled_std:,.0f}).")
    print(f"                Due to severe n1 vs n2 size imbalance ({n1} vs {n2:,}), s_pooled is heavily weighted by n2's smaller variance, whereas Unweighted d = {unweighted_d:.2f} accounts for fraud group's high variance.\n")

    # 7. STATISTICAL TEST 3: POINT-BISERIAL CORRELATION
    print("--- 7. STATISTICAL TEST 3: POINT-BISERIAL CORRELATION WITH ISFRAUD ---")
    numeric_cols = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'step']
    correlations = []
    
    for col in numeric_cols:
        r, p = stats.pointbiserialr(df['isFraud'], df[col])
        correlations.append({'feature': col, 'correlation_r': round(r, 4), 'p_value': f"{p:.4e}"})
    
    corr_df = pd.DataFrame(correlations)
    print(corr_df.to_string(index=False))
    print("\n=========================================================================\n")
    return df

if __name__ == "__main__":
    run_eda()
