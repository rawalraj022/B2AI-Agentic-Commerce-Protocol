"""Execution engine — validates and executes a payment against a credential.

This simulates the card authorization step. It enforces:
  - credential is ACTIVE
  - amount <= credential max
  - merchant matches credential
  - credential not expired
  - single use (ACTIVE -> USED)
"""
from datetime import datetime, timezone

from ..issuance.card import credential_service
from ..schemas import ExecutionResult


class Executor:
    """Executes a payment against a single-use credential."""

    def execute(self, credential_id: str, merchant: str, amount: float) -> ExecutionResult:
        credential = credential_service.get(credential_id)
        if credential is None:
            return ExecutionResult(status="FAILED", reason="Credential not found")

        if credential.status != "ACTIVE":
            return ExecutionResult(status="FAILED", reason="Credential already used")

        if credential.expires_at < datetime.now(timezone.utc):
            return ExecutionResult(status="FAILED", reason="Credential expired")

        if amount > credential.max_amount:
            return ExecutionResult(status="FAILED", reason="Amount exceeds authorization")

        if merchant != credential.merchant:
            return ExecutionResult(status="FAILED", reason="Merchant mismatch")

        # Single-use: mark as used.
        credential_service.use(credential_id)
        return ExecutionResult(status="SUCCESS")


executor = Executor()