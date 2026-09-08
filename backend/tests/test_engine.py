from types import SimpleNamespace
from app.evaluation.engine import evaluate
def flag(**kw):
    values={"key":"new_checkout","enabled":True,"default_value":False,"rollout_percentage":0,"rules":[]}; values.update(kw); return SimpleNamespace(**values)
def test_disabled_is_off(): assert evaluate(flag(enabled=False)).reason == "disabled"
def test_targeting_rule_wins():
 rule=SimpleNamespace(attribute="plan",operator="equals",value="premium",enabled_value=True)
 assert evaluate(flag(rules=[rule]),{"plan":"premium"}).reason == "targeting_rule"
def test_rollout_is_deterministic():
 f=flag(rollout_percentage=50); assert evaluate(f,{"id":"u123"}) == evaluate(f,{"id":"u123"})
def test_default_without_user(): assert evaluate(flag(default_value=True)).enabled is True
