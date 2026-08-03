"""
FastAPI Endpoint Integration Tests for VigilPay.
"""

import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_version" in data

def test_score_single_low_risk():
    payload = {
        "user_id": "C1001",
        "type": "PAYMENT",
        "amount": 45.0,
        "oldbalanceOrg": 500.0,
        "newbalanceOrig": 455.0,
        "nameDest": "M999",
        "oldbalanceDest": 1000.0,
        "newbalanceDest": 1045.0,
        "device_id": "DEV_101",
        "hour_of_day": 14,
        "minutes_since_last_txn": 120.0
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["LOW", "MEDIUM"]
    assert 0 <= data["risk_score"] <= 100
    assert len(data["shap_reasons"]) == 3

def test_score_single_high_risk():
    payload = {
        "user_id": "C1001",
        "type": "TRANSFER",
        "amount": 500000.0,
        "oldbalanceOrg": 500000.0,
        "newbalanceOrig": 0.0,
        "nameDest": "C999",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 500000.0,
        "device_id": "DEV_999",
        "hour_of_day": 3,
        "minutes_since_last_txn": 1.0
    }
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["MEDIUM", "HIGH"]
    assert data["risk_score"] >= 35.0
    assert len(data["rule_reasons"]) > 0

def test_score_batch_csv():
    df_sample = pd.DataFrame([
        {"transaction_id": "T1", "type": "PAYMENT", "amount": 25.0, "device_id": "DEV_101", "hour_of_day": 12},
        {"transaction_id": "T2", "type": "TRANSFER", "amount": 800000.0, "device_id": "DEV_999", "hour_of_day": 3}
    ])
    csv_bytes = df_sample.to_csv(index=False).encode("utf-8")
    
    response = client.post(
        "/score-batch",
        files={"file": ("test_batch.csv", io.BytesIO(csv_bytes), "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["transaction_id"] == "T1"
    assert data[1]["transaction_id"] == "T2"
