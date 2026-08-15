"""Approval store — Visa-style human-in-the-loop confirmation flow.

Implements `request_purchase_confirmation` -> `confirm_purchase`:
the agent proposes a purchase, the user reviews the explicit parameters
(max amount, merchant, expiry) and confirms or declines. The agent cannot
proceed until the user approves — the human retains control.
"""
from datetime import datetime, timezone
from typing import Optional

from ..config import settings
from ..schemas import PurchaseProposal


class ApprovalStore:
    """Tracks pending purchase proposals awaiting user confirmation."""

    def __init__(self):
        self._store: dict[str, PurchaseProposal] = {}
        self._counter = 0

    def create(self, proposal: PurchaseProposal) -> PurchaseProposal:
        self._counter += 1
        proposal.request_id = f"REQ-{self._counter:04d}"
        proposal.status = "pending"
        proposal.created_at = datetime.now(timezone.utc)
        self._store[proposal.request_id] = proposal
        return proposal

    def get(self, request_id: str) -> Optional[PurchaseProposal]:
        return self._store.get(request_id)

    def confirm(self, request_id: str) -> PurchaseProposal:
        proposal = self.get(request_id)
        if proposal is None:
            raise KeyError("Approval request not found")
        proposal.status = "approved"
        return proposal

    def decline(self, request_id: str) -> PurchaseProposal:
        proposal = self.get(request_id)
        if proposal is None:
            raise KeyError("Approval request not found")
        proposal.status = "declined"
        return proposal

    def list_pending(self) -> list[PurchaseProposal]:
        return [p for p in self._store.values() if p.status == "pending"]


approval_store = ApprovalStore()


class ApprovalService:
    """Gatekeeper that enforces human review before any spend."""

    def __init__(self, auto_approve: Optional[bool] = None):
        self.auto_approve = auto_approve if auto_approve is not None else settings.auto_approve

    def request_confirmation(
        self,
        merchant: str,
        amount: float,
        currency: str,
        mandate_id: str,
        agent_id: str,
        sku: str,
    ) -> PurchaseProposal:
        """Visa-style `request_purchase_confirmation`."""
        proposal = PurchaseProposal(
            merchant=merchant,
            amount=amount,
            currency=currency,
            mandate_id=mandate_id,
            agent_id=agent_id,
            sku=sku,
        )
        if self.auto_approve:
            return approval_store.create(proposal)  # record it; caller proceeds
        return approval_store.create(proposal)

    def confirm_purchase(self, request_id: str) -> PurchaseProposal:
        """Visa-style `confirm_purchase`."""
        return approval_store.confirm(request_id)

    def decline_purchase(self, request_id: str) -> PurchaseProposal:
        return approval_store.decline(request_id)


approval_service = ApprovalService()