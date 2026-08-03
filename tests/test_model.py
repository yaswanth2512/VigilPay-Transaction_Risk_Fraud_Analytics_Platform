"""
Unit Tests for VigilPay ML Model & SHAP Explainability Engine.
"""

import pytest
import os
from scoring.model import VigilPayMLModel

def test_model_training_and_shap():
    engine = VigilPayMLModel()
    auc, pr_auc = engine.train()
    
    assert auc > 0.50, f"ROC-AUC should be meaningfully above 0.50, got {auc}"
    assert pr_auc > 0.50, f"PR-AUC should be meaningfully above 0.50, got {pr_auc}"
    assert engine.is_trained
    assert engine.explainer is not None

def test_predict_and_explain_normal_txn():
    engine = VigilPayMLModel()
    engine.load()

    normal_txn = {
        "amount": 50.0,
        "oldbalanceOrg": 500.0,
        "newbalanceOrig": 450.0,
        "oldbalanceDest": 1000.0,
        "newbalanceDest": 1050.0,
        "device_id": "DEV_100",
        "hour_of_day": 12
    }
    baseline = {
        "user_avg_amount": 100.0,
        "user_primary_device": "DEV_100",
        "user_usual_hour": 12
    }

    prob, reasons = engine.predict_and_explain(normal_txn, baseline)
    assert 0.0 <= prob <= 1.0
    assert len(reasons) == 3
    assert isinstance(reasons[0], str)

def test_predict_and_explain_risky_txn():
    engine = VigilPayMLModel()
    engine.load()

    risky_txn = {
        "amount": 500000.0,
        "oldbalanceOrg": 500000.0,
        "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 500000.0,
        "device_id": "DEV_999",
        "hour_of_day": 3
    }
    baseline = {
        "user_avg_amount": 200.0,
        "user_primary_device": "DEV_100",
        "user_usual_hour": 14
    }

    prob, reasons = engine.predict_and_explain(risky_txn, baseline)
    assert prob > 0.50, f"High risk transaction should yield probability > 0.50, got {prob}"
    assert len(reasons) == 3
