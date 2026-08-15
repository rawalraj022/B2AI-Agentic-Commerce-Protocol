"""Policy engine tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.policy.policy_engine import PolicyEngine


def test_valid_payment_approved():
    engine = PolicyEngine(max_transaction=100, daily_limit=500, allowed_merchants=["Nike"])
    decision = engine.authorize("Nike", 40, "XSGD")
    assert decision.approved is True


def test_amount_too_high_denied():
    engine = PolicyEngine(max_transaction=100, daily_limit=500, allowed_merchants=["Nike"])
    decision = engine.authorize("Nike", 150, "XSGD")
    assert decision.approved is False


def test_unauthorized_merchant_denied():
    engine = PolicyEngine(max_transaction=100, daily_limit=500, allowed_merchants=["Nike"])
    decision = engine.authorize("Unknown Merchant", 40, "XSGD")
    assert decision.approved is False


def test_wrong_currency_denied():
    engine = PolicyEngine(max_transaction=100, daily_limit=500, allowed_merchants=["Nike"])
    decision = engine.authorize("Nike", 40, "USD")
    assert decision.approved is False