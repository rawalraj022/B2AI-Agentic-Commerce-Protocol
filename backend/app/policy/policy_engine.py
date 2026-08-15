"""Policy Engine — the guardrail that limits what an AI agent may spend.

This is a critical component: it ensures the LLM does NOT have unrestricted
spending authority. Every transaction must pass policy before authorization.
"""
from datetime import datetime, timezone
from typing import Optional

from ..config import settings
from ..schemas import PolicyDecision


class PolicyEngine:
    """Evaluates a proposed transaction against a wallet's policy."""

    def __init__(
        self,
        max_transaction: Optional[float] = None,
        daily_limit: Optional[float] = None,
        allowed_merchants: Optional[list[str]] = None,
        currency: Optional[str] = None,
    ):
        self.max_transaction = max_transaction or settings.default_max_transaction
        self.daily_limit = daily_limit or settings.default_daily_limit
        self.allowed_merchants = allowed_merchants or settings.allowed_merchants
        self.currency = currency or settings.default_currency

    def authorize(self, merchant: str, amount: float, currency: str = "XSGD") -> PolicyDecision:
        """Return an approve/deny decision with a list of individual checks."""
        checks: list[dict] = []

        # Check 1: merchant allowed
        merchant_ok = merchant in self.allowed_merchants
        checks.append(
            {
                "check": "merchant",
                "passed": merchant_ok,
                "detail": f"Merchant '{merchant}' {'allowed' if merchant_ok else 'not in allowed list'}",
            }
        )

        # Check 2: amount within max transaction
        amount_ok = amount <= self.max_transaction
        checks.append(
            {
                "check": "max_transaction",
                "passed": amount_ok,
                "detail": f"Amount {amount} {'within' if amount_ok else 'exceeds'} limit {self.max_transaction}",
            }
        )

        # Check 3: currency allowed
        currency_ok = currency == self.currency
        checks.append(
            {
                "check": "currency",
                "passed": currency_ok,
                "detail": f"Currency '{currency}' {'allowed' if currency_ok else 'not allowed'}",
            }
        )

        # Check 4: daily limit (simplified — no historical aggregation in MVP)
        daily_ok = amount <= self.daily_limit
        checks.append(
            {
                "check": "daily_limit",
                "passed": daily_ok,
                "detail": f"Amount {amount} {'within' if daily_ok else 'exceeds'} daily limit {self.daily_limit}",
            }
        )

        approved = all(c["passed"] for c in checks)
        reason = "Approved" if approved else "Denied by policy"
        return PolicyDecision(approved=approved, reason=reason, checks=checks)


# Default engine bound to configured policy.
policy_engine = PolicyEngine()