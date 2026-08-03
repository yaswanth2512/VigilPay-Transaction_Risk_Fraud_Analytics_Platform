"""
ML Model & SHAP Explainability Engine for VigilPay.

DATASET STRATEGY ARCHITECTURE (INTERVIEW TALKING POINT):
  - `paysim_sample.csv` (100k natural ratio): Reporting & EDA truth preserving the natural ~0.13%
    fraud rate so dashboard metrics, Chi-Square, and SQL queries present unskewed business truth.
  - `model_train_dataset.csv` (~41k 1:4 ratio): Model fitting set combining ALL ~8.2k real fraud cases
    from the full PaySim dataset with ~32.8k randomly undersampled non-fraud records.

MODEL ARCHITECTURE:
  - Default: scikit-learn `LogisticRegression(class_weight='balanced')`
  - Explainability: `shap.LinearExplainer` producing top 3 plain-language feature attributions per transaction.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score
)
import shap

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "vigilpay_model.pkl")
DATA_DIR = os.path.join(os.path.dirname(MODEL_DIR), "data")
MODEL_TRAIN_CSV = os.path.join(DATA_DIR, "model_train_dataset.csv")
REPORTING_CSV = os.path.join(DATA_DIR, "paysim_sample.csv")

FEATURE_COLS = [
    'amount',
    'amount_to_avg_ratio',
    'is_new_device',
    'hour_diff',
    'balance_delta_orig',
    'balance_delta_dest'
]

FEATURE_LABELS = {
    'amount': 'Transaction Amount',
    'amount_to_avg_ratio': 'Amount vs User Average Multiplier',
    'is_new_device': 'Unseen / New Device Flag',
    'hour_diff': 'Deviation from Usual Active Hours',
    'balance_delta_orig': 'Sender Balance Drain Amount',
    'balance_delta_dest': 'Recipient Balance Increase'
}

class VigilPayMLModel:
    def __init__(self):
        self.model = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.explainer = None
        self.is_trained = False

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineers required ML input features from raw dataset."""
        df_feat = df.copy()
        
        if 'amount_to_avg_ratio' not in df_feat.columns:
            user_avg = df_feat.groupby('nameOrig')['amount'].transform('mean')
            df_feat['amount_to_avg_ratio'] = df_feat['amount'] / (user_avg + 1e-5)
            
        if 'is_new_device' not in df_feat.columns:
            df_feat['is_new_device'] = np.random.choice([0, 1], size=len(df_feat), p=[0.9, 0.1])
            
        if 'hour_diff' not in df_feat.columns:
            df_feat['hour_diff'] = np.abs(df_feat['hour_of_day'] - 12) if 'hour_of_day' in df_feat.columns else 0
            
        if 'balance_delta_orig' not in df_feat.columns:
            df_feat['balance_delta_orig'] = df_feat['oldbalanceOrg'] - df_feat['newbalanceOrig']
            
        if 'balance_delta_dest' not in df_feat.columns:
            df_feat['balance_delta_dest'] = df_feat['newbalanceDest'] - df_feat['oldbalanceDest']

        return df_feat[FEATURE_COLS].fillna(0)

    def train(self, train_csv_path: str = MODEL_TRAIN_CSV):
        if not os.path.exists(train_csv_path):
            print(f"[!] Model training set missing at {train_csv_path}. Building datasets first...")
            sys.path.append(DATA_DIR)
            from generate_sample import create_reporting_and_training_datasets
            _, train_csv_path = create_reporting_and_training_datasets()

        print(f"[+] Training VigilPay Model on Dedicated Training Set: {train_csv_path}")
        df = pd.read_csv(train_csv_path)
        X = self.prepare_features(df)
        y = df['isFraud'].values

        print(f"    Training Dataset Records : {len(df):,}")
        print(f"    Total Fraud Cases        : {y.sum():,} ({y.mean()*100:.2f}%)")

        # Stratified 80/20 train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Fit Logistic Regression
        self.model.fit(X_train_scaled, y_train)

        # Predict & Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_prob = self.model.predict_proba(X_test_scaled)[:, 1]

        auc = roc_auc_score(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        print("\n=========================================================================")
        print("               VIGILPAY — MODEL EVALUATION REPORT                        ")
        print("=========================================================================")
        print(f"Dataset Strategy   : Dedicated Training Set (~1:4 Fraud Ratio)")
        print(f"Model Architecture : LogisticRegression(class_weight='balanced')")
        print(f"ROC-AUC Score      : {auc:.4f}")
        print(f"PR-AUC Score       : {pr_auc:.4f} (Precision-Recall Area Under Curve)")
        print(f"Precision          : {prec:.4f}")
        print(f"Recall             : {rec:.4f}")
        print(f"F1-Score           : {f1:.4f}")
        print("=========================================================================\n")

        # Initialize SHAP LinearExplainer
        self.explainer = shap.LinearExplainer(self.model, X_train_scaled)
        self.is_trained = True

        # Save trained artifacts
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler, 'explainer': self.explainer}, f)
        print(f"[OK] Model & SHAP explainer saved to: {MODEL_FILE}")
        return auc, pr_auc

    def load(self):
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.explainer = data['explainer']
                self.is_trained = True
            return True
        return False

    def predict_and_explain(self, txn: dict, baseline: dict) -> tuple:
        """
        Given transaction and baseline dicts, returns (fraud_probability, top_3_reasons).
        """
        if not self.is_trained:
            if not self.load():
                self.train()

        amount = float(txn.get('amount', 0))
        user_avg = float(baseline.get('user_avg_amount', 1000) or 1000)
        amount_ratio = amount / user_avg if user_avg > 0 else 1.0
        is_new_dev = 1 if str(txn.get('device_id')) != str(baseline.get('user_primary_device')) else 0
        hour_diff = abs(int(txn.get('hour_of_day', 12)) - int(baseline.get('user_usual_hour', 12) or 12))
        bal_delta_orig = float(txn.get('oldbalanceOrg', 0)) - float(txn.get('newbalanceOrig', 0))
        bal_delta_dest = float(txn.get('newbalanceDest', 0)) - float(txn.get('oldbalanceDest', 0))

        feat_array = np.array([[amount, amount_ratio, is_new_dev, hour_diff, bal_delta_orig, bal_delta_dest]])
        feat_scaled = self.scaler.transform(feat_array)

        prob = float(self.model.predict_proba(feat_scaled)[0, 1])

        # Calculate SHAP values
        shap_vals = self.explainer.shap_values(feat_scaled)[0]
        
        # Rank features by absolute SHAP contribution
        top_indices = np.argsort(np.abs(shap_vals))[::-1][:3]
        
        reasons = []
        for idx in top_indices:
            feat_name = FEATURE_COLS[idx]
            label = FEATURE_LABELS[feat_name]
            val = feat_array[0, idx]
            shap_v = shap_vals[idx]
            
            direction = "increased" if shap_v > 0 else "decreased"
            reasons.append(f"{label} ({val:,.2f}) {direction} risk score (SHAP impact: {shap_v:+.4f})")

        return prob, reasons

# Global singleton
ml_engine = VigilPayMLModel()

if __name__ == "__main__":
    ml_engine.train()
