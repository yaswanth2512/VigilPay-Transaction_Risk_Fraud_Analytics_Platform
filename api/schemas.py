"""
Pydantic Schemas for VigilPay Scoring API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TransactionInput(BaseModel):
    transaction_id: Optional[str] = Field(default=None, description="Optional unique identifier for transaction")
    user_id: str = Field(default="C1001", description="Customer ID")
    type: str = Field(default="TRANSFER", description="Transaction Type (TRANSFER, CASH_OUT, PAYMENT, etc.)")
    amount: float = Field(default=100.0, description="Transaction Amount in USD")
    oldbalanceOrg: float = Field(default=1000.0, description="Sender balance before transaction")
    newbalanceOrig: float = Field(default=900.0, description="Sender balance after transaction")
    nameDest: str = Field(default="M2001", description="Recipient account or merchant ID")
    oldbalanceDest: float = Field(default=0.0, description="Recipient balance before transaction")
    newbalanceDest: float = Field(default=100.0, description="Recipient balance after transaction")
    device_id: str = Field(default="DEV_101", description="Device ID used")
    hour_of_day: int = Field(default=14, description="Hour of transaction (0-23)")
    minutes_since_last_txn: Optional[float] = Field(default=60.0, description="Minutes since user's prior transaction")

class BaselineInput(BaseModel):
    user_avg_amount: Optional[float] = 100.0
    user_primary_device: Optional[str] = "DEV_101"
    user_usual_hour: Optional[int] = 14

class RiskAssessmentOutput(BaseModel):
    transaction_id: str
    risk_score: float = Field(description="Combined risk score from 0 to 100")
    risk_level: str = Field(description="Risk Level: LOW, MEDIUM, or HIGH")
    ml_fraud_probability: float = Field(description="ML Model Fraud Probability (0 to 1)")
    rule_penalty_score: float = Field(description="Rule Engine penalty points")
    rule_reasons: List[str] = Field(description="Rule flags triggered")
    shap_reasons: List[str] = Field(description="Top 3 SHAP feature attributions")
    all_reasons: List[str] = Field(description="Combined plain-language explanation reasons")

class HealthCheckOutput(BaseModel):
    status: str
    model_version: str
    engine_status: str
