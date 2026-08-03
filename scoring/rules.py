"""
Deterministic Rule Engine for VigilPay.
Evaluates 4 transparent business risk rules before ML scoring.
Each rule function returns (triggered: bool, reason: str, penalty_score: float).
"""

from typing import Dict, Any, Tuple, List

def rule_amount_10x_baseline(transaction: Dict[str, Any], baseline: Dict[str, Any]) -> Tuple[bool, str, float]:
    """Triggers if transaction amount is over 10x user's historical average amount."""
    amount = float(transaction.get("amount", 0))
    user_avg = float(baseline.get("user_avg_amount", 1000.0) or 1000.0)
    
    if user_avg > 0 and amount > (10 * user_avg):
        reason = f"Transaction amount (${amount:,.2f}) is over 10x user average (${user_avg:,.2f})."
        return True, reason, 35.0
    return False, "", 0.0

def rule_new_device(transaction: Dict[str, Any], baseline: Dict[str, Any]) -> Tuple[bool, str, float]:
    """Triggers if device ID is new or differs from user's primary historical device."""
    current_device = str(transaction.get("device_id", "")).strip()
    primary_device = str(baseline.get("user_primary_device", "")).strip()
    
    if current_device and primary_device and current_device != primary_device:
        reason = f"Unseen device '{current_device}' used (user primary device: '{primary_device}')."
        return True, reason, 25.0
    return False, "", 0.0

def rule_unusual_hour(transaction: Dict[str, Any], baseline: Dict[str, Any]) -> Tuple[bool, str, float]:
    """Triggers if transaction hour differs by more than 4 hours from user usual active hour."""
    current_hour = int(transaction.get("hour_of_day", 12))
    usual_hour = int(baseline.get("user_usual_hour", 12) or 12)
    
    hour_diff = abs(current_hour - usual_hour)
    # Handle midnight wraparound (e.g. 23 vs 1 is 2 hours diff)
    hour_diff = min(hour_diff, 24 - hour_diff)
    
    if hour_diff > 4:
        reason = f"Transaction hour ({current_hour:02d}:00) is outside user usual active window ({usual_hour:02d}:00 ± 4h)."
        return True, reason, 20.0
    return False, "", 0.0

def rule_rapid_transactions(transaction: Dict[str, Any], baseline: Dict[str, Any]) -> Tuple[bool, str, float]:
    """Triggers if transaction velocity is high (time since last transaction < 5 minutes)."""
    minutes_since_last = float(transaction.get("minutes_since_last_txn", 999.0) or 999.0)
    
    if minutes_since_last < 5.0:
        reason = f"Rapid repeated transaction detected ({minutes_since_last:.1f} min since previous transaction)."
        return True, reason, 30.0
    return False, "", 0.0

def evaluate_all_rules(transaction: Dict[str, Any], baseline: Dict[str, Any]) -> Tuple[float, List[str], List[Dict[str, Any]]]:
    """
    Evaluates all 4 rules and returns (total_rule_penalty, triggered_reasons, rule_details).
    """
    rules = [
        rule_amount_10x_baseline,
        rule_new_device,
        rule_unusual_hour,
        rule_rapid_transactions
    ]
    
    total_penalty = 0.0
    reasons = []
    rule_details = []
    
    for rule_fn in rules:
        triggered, reason, penalty = rule_fn(transaction, baseline)
        rule_details.append({
            "rule_name": rule_fn.__name__,
            "triggered": triggered,
            "reason": reason,
            "penalty": penalty
        })
        if triggered:
            total_penalty += penalty
            reasons.append(reason)
            
    return min(100.0, total_penalty), reasons, rule_details
