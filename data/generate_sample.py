"""
Dataset Generation & Sampling Suite for VigilPay.
Maintains two distinct dataset strategies:
  1. `paysim_sample.csv` (100k natural ratio): Reporting & EDA truth preserving ~0.13% natural fraud rate.
  2. `model_train_dataset.csv` (~41k balanced ratio): Model fitting set combining ALL ~8.2k real fraud cases
     with ~1:4 undersampled non-fraud records (~32.8k).
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from download_paysim import get_paysim_dataset

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "paysim_sample.csv")
MODEL_TRAIN_CSV_PATH = os.path.join(DATA_DIR, "model_train_dataset.csv")

def create_reporting_and_training_datasets(sample_size=100000):
    raw_path = get_paysim_dataset()
    print(f"[+] Loading raw dataset from: {raw_path}")
    df = pd.read_csv(raw_path)
    
    print(f"    Full Raw Dataset Size: {len(df):,} rows")
    total_fraud_count = df['isFraud'].sum()
    print(f"    Full Raw Fraud Count : {total_fraud_count:,} ({df['isFraud'].mean()*100:.3f}%)")

    # =========================================================================
    # 1. REPORTING / EDA DATASET (paysim_sample.csv) - Natural Imbalance (~0.13%)
    # =========================================================================
    if len(df) <= sample_size:
        sample_df = df.copy()
    else:
        fraud_df = df[df['isFraud'] == 1]
        non_fraud_df = df[df['isFraud'] == 0]
        
        fraud_ratio = len(fraud_df) / len(df)
        sample_fraud_count = int(sample_size * fraud_ratio)
        sample_non_fraud_count = sample_size - sample_fraud_count
        
        sampled_fraud = fraud_df.sample(n=min(len(fraud_df), sample_fraud_count), random_state=42)
        sampled_non_fraud = non_fraud_df.sample(n=sample_non_fraud_count, random_state=42)
        
        sample_df = pd.concat([sampled_fraud, sampled_non_fraud]).sample(frac=1, random_state=42).reset_index(drop=True)

    # Enrich features for reporting set
    sample_df = _enrich_features(sample_df)
    sample_df.to_csv(SAMPLE_CSV_PATH, index=False)
    print(f"\n[OK] 1. Reporting/EDA Dataset Created: {SAMPLE_CSV_PATH}")
    print(f"     Size: {len(sample_df):,} rows | Fraud: {sample_df['isFraud'].sum():,} ({sample_df['isFraud'].mean()*100:.3f}%)")

    # =========================================================================
    # 2. MODEL TRAINING DATASET (model_train_dataset.csv) - Undersampled (~1:4 Ratio)
    # =========================================================================
    all_fraud = df[df['isFraud'] == 1].copy()
    all_non_fraud = df[df['isFraud'] == 0].copy()

    # 1:4 Fraud to Non-Fraud ratio
    target_non_fraud_count = min(len(all_non_fraud), len(all_fraud) * 4)
    sampled_non_fraud_for_train = all_non_fraud.sample(n=target_non_fraud_count, random_state=42)

    model_train_df = pd.concat([all_fraud, sampled_non_fraud_for_train]).sample(frac=1, random_state=42).reset_index(drop=True)
    model_train_df = _enrich_features(model_train_df)
    model_train_df.to_csv(MODEL_TRAIN_CSV_PATH, index=False)

    print(f"\n[OK] 2. Model Training Dataset Created: {MODEL_TRAIN_CSV_PATH}")
    print(f"     Size: {len(model_train_df):,} rows | All Fraud: {model_train_df['isFraud'].sum():,} | Non-Fraud: {len(model_train_df)-model_train_df['isFraud'].sum():,} (Ratio ~1:4)")
    print("="*75)
    return SAMPLE_CSV_PATH, MODEL_TRAIN_CSV_PATH

def _enrich_features(df):
    """Adds device IDs, timestamps, and transaction IDs."""
    if 'device_id' not in df.columns:
        unique_users = df['nameOrig'].unique()
        user_primary_device = {u: f"DEV_{np.random.randint(100, 999)}" for u in unique_users}
        devices = [user_primary_device[u] if np.random.rand() < 0.90 else f"DEV_{np.random.randint(100, 999)}" for u in df['nameOrig']]
        df['device_id'] = devices

    base_date = datetime(2025, 1, 1, 0, 0, 0)
    df['txn_timestamp'] = df['step'].apply(
        lambda step: (base_date + timedelta(hours=int(step), minutes=int(np.random.randint(0, 60)))).strftime('%Y-%m-%d %H:%M:%S')
    )
    df['txn_date'] = df['txn_timestamp'].apply(lambda x: str(x).split(' ')[0])
    df['hour_of_day'] = df['txn_timestamp'].apply(lambda x: int(str(x).split(' ')[1].split(':')[0]))

    if 'transaction_id' not in df.columns:
        df['transaction_id'] = [f"TXN_{100000 + i}" for i in range(len(df))]
    return df

if __name__ == "__main__":
    create_reporting_and_training_datasets()
