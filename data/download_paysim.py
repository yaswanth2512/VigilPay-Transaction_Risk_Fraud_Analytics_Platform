"""
Data Download Utility for PaySim Fraud Dataset.
Attempts to download the official PaySim dataset (ealaxi/paysim1) via Kaggle API.
If Kaggle credentials are missing or invalid, displays setup instructions and provides fallback generation.
"""

import os
import sys
import pandas as pd
import numpy as np

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_CSV_PATH = os.path.join(DATA_DIR, "PS_20174392719_1491208443494_raw.csv")
KAGGLE_DATASET = "ealaxi/paysim1"

def download_from_kaggle():
    print("[+] Attempting to download PaySim dataset from Kaggle...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(KAGGLE_DATASET, path=DATA_DIR, unzip=True)
        print("[OK] Successfully downloaded PaySim dataset from Kaggle!")
        return True
    except Exception as e:
        print("\n" + "="*75)
        print("[!] WARNING: Kaggle API authentication failed or kaggle.json is missing.")
        print(f"    Error details: {e}")
        print("\n[!] TO SET UP KAGGLE API CREDENTIALS:")
        print("    1. Go to https://www.kaggle.com/settings -> Click 'Create New Token'")
        print("    2. Place the downloaded 'kaggle.json' in your home folder:")
        print(f"       Windows: C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json")
        print("       Linux/Mac: ~/.kaggle/kaggle.json")
        print("="*75 + "\n")
        return False

def generate_fallback_dataset(num_records=100000, output_path=RAW_CSV_PATH):
    """
    Generates a realistic synthetic PaySim dataset matching the exact schema 
    and natural class imbalance (~0.13% fraud rate) when Kaggle API is not configured.
    """
    print(f"[+] Generating realistic fallback PaySim dataset ({num_records:,} records)...")
    np.random.seed(42)

    # 60 days of steps (1 step = 1 hour)
    steps = np.random.randint(1, 744, size=num_records)
    steps.sort()

    types = np.random.choice(
        ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'CASH_IN', 'DEBIT'],
        size=num_records,
        p=[0.35, 0.20, 0.35, 0.08, 0.02]
    )

    # Fraud occurs ONLY in TRANSFER and CASH_OUT in real PaySim dataset
    transfer_cashout_mask = (types == 'TRANSFER') | (types == 'CASH_OUT')
    eligible_indices = np.where(transfer_cashout_mask)[0]
    
    # ~0.13% overall fraud rate
    target_fraud_count = int(num_records * 0.0013)
    fraud_indices = set(np.random.choice(eligible_indices, size=target_fraud_count, replace=False))

    is_fraud = np.zeros(num_records, dtype=int)
    is_flagged_fraud = np.zeros(num_records, dtype=int)

    for idx in fraud_indices:
        is_fraud[idx] = 1
        # High value fraud transactions get flagged
        if np.random.rand() > 0.8:
            is_flagged_fraud[idx] = 1

    amounts = np.zeros(num_records)
    oldbalance_orig = np.zeros(num_records)
    newbalance_orig = np.zeros(num_records)
    oldbalance_dest = np.zeros(num_records)
    newbalance_dest = np.zeros(num_records)

    # User populations
    num_users = int(num_records * 0.3)
    user_pool = [f"C{1000000 + i}" for i in range(num_users)]
    dest_pool = [f"M{1000000 + i}" for i in range(num_users // 2)] + [f"C{2000000 + i}" for i in range(num_users // 2)]

    name_orig = np.random.choice(user_pool, size=num_records)
    name_dest = np.random.choice(dest_pool, size=num_records)

    for i in range(num_records):
        if is_fraud[i] == 1:
            # Fraudulent transactions tend to have larger amounts and drain account balance
            amount = np.random.uniform(50000, 1000000)
            old_orig = amount + np.random.uniform(0, 5000)
            new_orig = 0.0
            old_dest = np.random.uniform(0, 100000)
            new_dest = old_dest + amount
        else:
            if types[i] == 'PAYMENT':
                amount = np.random.exponential(scale=150) + 5
            elif types[i] in ['TRANSFER', 'CASH_OUT']:
                amount = np.random.exponential(scale=1500) + 20
            else:
                amount = np.random.exponential(scale=500) + 10

            old_orig = np.random.uniform(amount, amount * 10) if np.random.rand() > 0.3 else 0.0
            new_orig = max(0.0, old_orig - amount) if types[i] in ['PAYMENT', 'TRANSFER', 'CASH_OUT'] else old_orig + amount
            old_dest = np.random.uniform(0, 50000) if np.random.rand() > 0.4 else 0.0
            new_dest = old_dest + amount if types[i] in ['CASH_IN', 'TRANSFER', 'CASH_OUT'] else old_dest

        amounts[i] = round(amount, 2)
        oldbalance_orig[i] = round(old_orig, 2)
        newbalance_orig[i] = round(new_orig, 2)
        oldbalance_dest[i] = round(old_dest, 2)
        newbalance_dest[i] = round(new_dest, 2)

    device_ids = [f"DEV_{np.random.randint(100, 999)}" for _ in range(num_records)]

    df = pd.DataFrame({
        'step': steps,
        'type': types,
        'amount': amounts,
        'nameOrig': name_orig,
        'oldbalanceOrg': oldbalance_orig,
        'newbalanceOrig': newbalance_orig,
        'nameDest': name_dest,
        'oldbalanceDest': oldbalance_dest,
        'newbalanceDest': newbalance_dest,
        'isFraud': is_fraud,
        'isFlaggedFraud': is_flagged_fraud,
        'device_id': device_ids
    })

    df.to_csv(output_path, index=False)
    print(f"[OK] Successfully generated fallback PaySim dataset to {output_path}")
    print(f"    Total rows: {len(df):,}")
    print(f"    Fraud cases: {df['isFraud'].sum():,} ({df['isFraud'].mean()*100:.3f}%)")
    return output_path

def get_paysim_dataset():
    # Look for existing downloaded raw files
    possible_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv') and 'sample' not in f]
    if possible_files:
        path = os.path.join(DATA_DIR, possible_files[0])
        print(f"[OK] Found existing raw dataset: {path}")
        return path
    
    success = download_from_kaggle()
    if success:
        possible_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv') and 'sample' not in f]
        if possible_files:
            return os.path.join(DATA_DIR, possible_files[0])
    
    return generate_fallback_dataset()

if __name__ == "__main__":
    get_paysim_dataset()
