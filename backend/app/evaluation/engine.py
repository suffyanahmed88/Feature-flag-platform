import hashlib
from dataclasses import dataclass
@dataclass
class Evaluation: enabled: bool; reason: str
def evaluate(flag, user=None):
    if not flag.enabled: return Evaluation(False,"disabled")
    data=user or {}
    for rule in flag.rules:
        actual=data.get("id" if rule.attribute=="user_id" else rule.attribute)
        matched=(actual==rule.value) if rule.operator=="equals" else (actual is not None and actual!=rule.value)
        if matched: return Evaluation(rule.enabled_value,"targeting_rule")
    uid=data.get("id")
    if uid and flag.rollout_percentage:
        bucket=int(hashlib.sha256(f"{flag.key}:{uid}".encode()).hexdigest(),16)%100
        return Evaluation(bucket < flag.rollout_percentage,"percentage_rollout")
    return Evaluation(flag.default_value,"default")
