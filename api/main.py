"""
FastAPI Scoring Service for VigilPay.
Exposes POST /score, POST /score-batch, and GET /health.
Integrates Rule Engine + ML Model + SHAP explainability.
"""

import os
import sys
import io
import pandas as pd
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Adjust paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from scoring.rules import evaluate_all_rules
from scoring.model import VigilPayMLModel
from api.schemas import TransactionInput, RiskAssessmentOutput, HealthCheckOutput

app = FastAPI(
    title="VigilPay — Transaction Risk & Fraud Analytics API",
    description="Explainable Fraud Risk Scoring API combining Rule Engine, ML & SHAP",
    version="1.0.0"
)

# Enable CORS for Streamlit Cloud & local cross-origin calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML Engine
ml_engine = VigilPayMLModel()

@app.on_event("startup")
def startup_event():
    if not ml_engine.load():
        print("[+] Training ML model on startup...")
        ml_engine.train()

@app.get("/health", response_model=HealthCheckOutput)
def health_check():
    return HealthCheckOutput(
        status="healthy",
        model_version="1.0.0 (LogisticRegression + SHAP)",
        engine_status="active"
    )

def compute_combined_risk(txn_dict: dict, baseline_dict: dict) -> RiskAssessmentOutput:
    # 1. Evaluate Rule Engine
    rule_score, rule_reasons, _ = evaluate_all_rules(txn_dict, baseline_dict)

    # 2. Evaluate ML Model & SHAP
    ml_prob, shap_reasons = ml_engine.predict_and_explain(txn_dict, baseline_dict)
    ml_score = ml_prob * 100.0

    # 3. Combine scores (60% ML probability + 40% Rule Penalty)
    combined_score = round(0.60 * ml_score + 0.40 * rule_score, 2)
    combined_score = min(100.0, max(0.0, combined_score))

    # Determine Risk Level
    if combined_score >= 70.0:
        risk_level = "HIGH"
    elif combined_score >= 35.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Merge reasons
    all_reasons = list(rule_reasons) + list(shap_reasons[:2])
    if not all_reasons:
        all_reasons = ["Transaction behavior aligns with historical user baseline parameters."]

    txn_id = str(txn_dict.get("transaction_id") or f"TXN_{pd.Timestamp.now().value // 10**6}")

    return RiskAssessmentOutput(
        transaction_id=txn_id,
        risk_score=combined_score,
        risk_level=risk_level,
        ml_fraud_probability=round(ml_prob, 4),
        rule_penalty_score=round(rule_score, 2),
        rule_reasons=rule_reasons,
        shap_reasons=shap_reasons,
        all_reasons=all_reasons
    )

@app.post("/score", response_model=RiskAssessmentOutput)
def score_single_transaction(txn: TransactionInput):
    txn_dict = txn.model_dump()
    # Baseline defaults
    baseline_dict = {
        "user_avg_amount": 100.0,
        "user_primary_device": "DEV_101",
        "user_usual_hour": 14
    }
    return compute_combined_risk(txn_dict, baseline_dict)

@app.post("/score-batch", response_model=List[RiskAssessmentOutput])
async def score_batch_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV format")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    required_cols = ["amount", "type"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV missing required columns: {missing}")

    results = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        baseline_dict = {
            "user_avg_amount": row_dict.get("user_avg_amount", 100.0),
            "user_primary_device": row_dict.get("user_primary_device", "DEV_101"),
            "user_usual_hour": row_dict.get("user_usual_hour", 14)
        }
        res = compute_combined_risk(row_dict, baseline_dict)
        results.append(res)

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
