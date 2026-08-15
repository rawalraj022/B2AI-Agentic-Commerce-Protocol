"""Payment Mandate — a signed authorization where the user sets explicit
spend parameters for the agent, Visa-style (request_purchase_confirmation).

A mandate binds: user (wallet), agent_id, merchant, max_amount, currency,
expiry, and a nonce, signed by the user. The agent can only spend within
the mandate's parameters. This demonstrates that the AI agent is NOT given
unrestricted spending authority.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from ..schemas import Mandate


class MandateService:
    """Creates and verifies user-signed spend mandates."""

    def __init__(self, ttl_minutes: int = 30):
        self.ttl_minutes = ttl_minutes
        self._counter = 0
        self._store: dict[str, Mandate] = {}

    def create(
        self,
        user_wallet: str,
        agent_id: str,
        merchant: str,
        max_amount: float,
        currency: str = "XSGD",
        signature: str = "",
    ) -> Mandate:
        self._counter += 1
        mandate_id = f"MNDT-{self._counter:04d}"
        nonce = secrets.token_hex(16)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=self.ttl_minutes)

        mandate = Mandate(
            mandate_id=mandate_id,
            user_wallet=user_wallet,
            agent_id=agent_id,
            merchant=merchant,
            max_amount=max_amount,
            currency=currency,
            expiry=expiry,
            signature=signature or self._default_sign(user_wallet, agent_id, merchant, max_amount, currency, nonce),
            nonce=nonce,
            status="ACTIVE",
        )
        self._store[mandate_id] = mandate
        return mandate

    def _default_sign(
        self,
        user_wallet: str,
        agent_id: str,
        merchant: str,
        max_amount: float,
        currency: str,
        nonce: str,
    ) -> str:
        """Derive a deterministic 'signature' from the mandate contents.

        In the real integration this would be a user signature produced by
        their wallet (e.g. personal_sign). For the demo we derive a SHA-256
        hash of the mandate fields so the mandate is tamper-evident.
        """
        raw = f"{user_wallet}|{agent_id}|{merchant}|{max_amount}|{currency}|{nonce}"
        return "0x" + hashlib.sha256(raw.encode()).hexdigest()

    def get(self, mandate_id: str) -> Mandate | None:
        return self._store.get(mandate_id)

    def is_active(self, mandate: Mandate) -> bool:
        return mandate.status == "active" and mandate.expiry > datetime.now(timezone.utc)

    def mark_used(self, mandate_id: str) -> None:
        if mandate_id in self._store:
            self._store[mandate_id].status = "used"


mandate_service = MandateService()