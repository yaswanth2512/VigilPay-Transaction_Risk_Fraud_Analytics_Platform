"""
Unit Tests for VigilPay Deterministic Rule Engine.
"""

import pytest
from scoring.rules import (
    rule_amount_10x_baseline,
    rule_new_device,
    rule_unusual_hour,
    rule_rapid_transactions,
    evaluate_all_rules
)

def test_rule_amount_10x_baseline():
    baseline = {"user_avg_amount": 100.0}
    
    # Normal transaction ($500 <= $1000)
    triggered, reason, score = rule_amount_10x_baseline({"amount": 500.0}, baseline)
    assert not triggered
    assert score == 0.0

    # Risky transaction ($1500 > $1000)
    triggered, reason, score = rule_amount_10x_baseline({"amount": 1500.0}, baseline)
    assert triggered
    assert score == 35.0
    assert "10x user average" in reason

def test_rule_new_device():
    baseline = {"user_primary_device": "DEV_123"}
    
    # Same device
    triggered, reason, score = rule_new_device({"device_id": "DEV_123"}, baseline)
    assert not triggered

    # New device
    triggered, reason, score = rule_new_device({"device_id": "DEV_999"}, baseline)
    assert triggered
    assert score == 25.0
    assert "DEV_999" in reason

def test_rule_unusual_hour():
    baseline = {"user_usual_hour": 14} # 2 PM
    
    # Usual hour (3 PM)
    triggered, reason, score = rule_unusual_hour({"hour_of_day": 15}, baseline)
    assert not triggered

    # Unusual hour (3 AM)
    triggered, reason, score = rule_unusual_hour({"hour_of_day": 3}, baseline)
    assert triggered
    assert score == 20.0

def test_rule_rapid_transactions():
    baseline = {}
    
    # Normal gap (30 minutes)
    triggered, reason, score = rule_rapid_transactions({"minutes_since_last_txn": 30.0}, baseline)
    assert not triggered

    # Rapid transaction (1 minute)
    triggered, reason, score = rule_rapid_transactions({"minutes_since_last_txn": 1.0}, baseline)
    assert triggered
    assert score == 30.0

def test_evaluate_all_rules_combined():
    baseline = {"user_avg_amount": 100.0, "user_primary_device": "DEV_100", "user_usual_hour": 12}
    txn = {
        "amount": 2000.0,            # Triggers 10x (+35)
        "device_id": "DEV_999",       # Triggers new device (+25)
        "hour_of_day": 3,             # Triggers unusual hour (+20)
        "minutes_since_last_txn": 2.0 # Triggers rapid (+30)
    }
    
    total_score, reasons, details = evaluate_all_rules(txn, baseline)
    assert total_score == 100.0 # capped at 100
    assert len(reasons) == 4
    assert len(details) == 4
