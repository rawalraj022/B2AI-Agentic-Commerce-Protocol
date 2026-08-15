"""Supervisor Agent — Visa-style agents-as-tools orchestration.

The SupervisorAgent routes sub-agent tool invocations for a given user intent.
It exposes a single entrypoint `route_intent` that the main /agent/intent
endpoint calls. The supervisor decides which toolchain to execute based on
the parsed intent, then dispatches to the appropriate sub-agent.

Available sub-tools:
  - shopping: product discovery + SKU resolution
  - discovery: catalog lookup
  - policy: spend guardrails
  - payment: credential issuance + authorization + settlement
"""
from typing import Literal, Optional

from ..agent.agent import agent
from ..approval.approval import approval_service
from ..authorization.authorization import authorization_service
from ..discovery.discovery import discovery
from ..execution.executor import Executor as _Executor
from ..issuance.card import credential_service
from ..mandate.mandate import mandate_service
from ..policy.policy_engine import policy_engine
from ..receipt.receipt import receipt_service
from ..schemas import Intent, PurchaseRequest, PurchaseResponse, TimelineStep
from ..settlement.settlement import settlement_service
from ..supervisor.directory_integration import get_directory, merchant_score, agent_trust
from ..wallet.wallet import wallet

executor_service = _Executor()

StepStatus = Literal["ok", "denied", "error"]


class TimelineEntry:
    """A single step in the orchestration timeline."""
    def __init__(self, step: str, status: StepStatus, detail: str, data: Optional[dict] = None):
        self.step = step
        self.status = status
        self.detail = detail
        self.data = data

    def model_dump(self) -> dict:
        return {
            "step": self.step,
            "status": self.status,
            "detail": self.detail,
            "data": self.data,
        }


class SupervisorAgent:
    """Visa-style supervisor that orchestrates AI agent tools.

    The flow for a purchase intent:
      1. shopping   → resolve product SKU from catalog
      2. discovery  → verify merchant + token-readiness
      3. policy     → enforce amount/currency/daily-limit guards
      4. payment    → issue credential → authorize → settle

    If any step denies, the supervisor stops and returns the denial reason.
    """

    def __init__(self):
        self.shopping_steps: list[TimelineEntry] = []
        self.discovery_steps: list[TimelineEntry] = []
        self.policy_steps: list[TimelineEntry] = []
        self.payment_steps: list[TimelineEntry] = []

    def _add(self, steps: list[TimelineEntry], entry: TimelineEntry) -> None:
        steps.append(entry)

    def route_intent(self, user_message: str, wallet_address: str = "") -> dict:
        """Parse intent and orchestrate the sub-agent toolchain.

        Returns a dict with:
          - success: bool
          - timeline: list[TimelineEntry]
          - receipt: optional Receipt dict
        """
        # 1. Parse the user's natural-language intent
        intent = agent.understand_intent(user_message)
        # Inject wallet_address if provided by the caller
        if wallet_address and wallet_address.strip():
            intent.wallet_address = wallet_address
        timeline: list[TimelineEntry] = []

        # --- Step 1: Intent + Shopping (product resolution) ---
        self._add(timeline, TimelineEntry(
            step="Intent",
            status="ok",
            detail=f"Understood: {intent.product} from {intent.merchant} for {intent.max_amount} {intent.currency}",
            data=intent.model_dump(),
        ))

        product = discovery.resolve(intent.product, intent.merchant)
        if product is None:
            self._add(timeline, TimelineEntry(
                step="Discovery", status="denied",
                detail="No matching SKU found in catalog",
            ))
            return {"success": False, "timeline": timeline}

        self._add(timeline, TimelineEntry(
            step="Discovery",
            status="ok",
            detail=f"SKU {product.sku} found: {product.name} at {product.price} {product.currency}",
            data=product.model_dump(),
        ))

        # --- Step 2: Policy guardrails ---
        decision = policy_engine.authorize(product.merchant, product.price, product.currency)
        if not decision.approved:
            self._add(timeline, TimelineEntry(
                step="Policy", status="denied",
                detail=decision.reason,
                data=decision.model_dump(),
            ))
            return {"success": False, "timeline": timeline}

        self._add(timeline, TimelineEntry(
            step="Policy",
            status="ok",
            detail="Policy approved: merchant, amount, currency, daily limit",
            data=decision.model_dump(),
        ))

        # --- Step 3: Payment (credential → authorization → execution → settlement) ---
        wallet_address = intent.wallet_address or wallet.get_settlement_address() or "0x0000000000000000000000000000000000000000"

        # Issue authorization
        auth = authorization_service.create(
            wallet_address=wallet_address,
            merchant=product.merchant,
            sku=product.sku,
            amount=product.price,
            currency=product.currency,
        )
        self._add(timeline, TimelineEntry(
            step="Authorization",
            status="ok",
            detail=f"Authorization {auth.authorization_id} created",
            data=auth.model_dump(),
        ))

        # Issue single-use credential
        credential = credential_service.issue(
            authorization_id=auth.authorization_id,
            merchant=product.merchant,
            max_amount=product.price,
        )
        self._add(timeline, TimelineEntry(
            step="Credential",
            status="ok",
            detail=f"Single-use credential {credential.credential_id} issued",
            data=credential.model_dump(),
        ))

        # Execute payment against credential
        execution = executor_service.execute(credential.credential_id, product.merchant, product.price)
        if execution.status != "SUCCESS":
            self._add(timeline, TimelineEntry(
                step="Execution", status="denied",
                detail=execution.reason or "Payment execution failed",
            ))
            return {"success": False, "timeline": timeline}

        self._add(timeline, TimelineEntry(
            step="Execution",
            status="ok",
            detail="Payment authorized against single-use credential",
        ))

        # Settle payment
        settlement = settlement_service.settle(wallet_address, product.price, product.currency)
        self._add(timeline, TimelineEntry(
            step="Settlement",
            status="ok",
            detail=f"{product.price} {product.currency} settled on {settlement.network}"
                   + (" (simulated)" if settlement.simulated else ""),
            data=settlement.model_dump(),
        ))

        # Build receipt
        receipt = receipt_service.build(
            authorization_id=auth.authorization_id,
            credential_id=credential.credential_id,
            merchant=product.merchant,
            sku=product.sku,
            amount=product.price,
            currency=product.currency,
            wallet_address=wallet_address,
            commitment=auth.commitment,
            transaction_hash=settlement.transaction_hash,
            network=settlement.network,
            simulated=settlement.simulated,
        )
        self._add(timeline, TimelineEntry(
            step="Receipt",
            status="ok",
            detail=f"Receipt generated: {receipt.authorization_id}",
            data=receipt.model_dump(),
        ))

        return {
            "success": True,
            "timeline": timeline,
            "receipt": receipt.model_dump(),
        }


# Global supervisor instance
supervisor = SupervisorAgent()
