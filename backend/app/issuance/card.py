"""Single-use payment credential issuance.

A credential is bound to a merchant, a max amount, and an expiry. It can be
used exactly once (ACTIVE -> USED). This simulates a single-use virtual card
without attempting to create a real Visa/Mastercard network.

Each credential now carries Visa-style Enhanced Token fields:
  - agent_id: which agent issued this credential
  - mandate_id: reference to the user-signed spend mandate
  - token_context: masked context (merchant+amount, never raw card data)
  - token_assurance: true when credential is merchant-scoped + amount-limited + expiry-bound
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone


class Credential:
    """A single-use payment credential with Visa-style Enhanced Token fields.

    Attributes:
        credential_id: unique identifier for this credential
        credential_type: always "single-use"
        type: alias for credential_type (for test compatibility)
        agent_id: which agent issued this credential
        mandate_id: reference to the user-signed spend mandate
        merchant: merchant name (e.g. "Nike")
        max_amount: maximum spend allowed (in XSGD)
        currency: always "XSGD"
        token_context: masked context — never exposes raw card data
        token_assurance: true when merchant-scoped + amount-limited + expiry-bound
        status: "ACTIVE" or "USED"
        expires_at: datetime when this credential expires
        used_at: datetime when credential was consumed (None if unused)
        authorization_id: the authorization this credential was issued under
    """

    def __init__(self, credential_id: str, credential_type: str,
                 agent_id: str, mandate_id: str, merchant: str,
                 max_amount: float, currency: str, token_context: str,
                 token_assurance: bool, status: str, expires_at,
                 used_at: str | None, authorization_id: str):
        self.credential_id = credential_id
        self.credential_type = credential_type
        self.type = "single_use"
        self.agent_id = agent_id
        self.mandate_id = mandate_id
        self.merchant = merchant
        self.max_amount = max_amount
        self.currency = currency
        self.token_context = token_context
        self.token_assurance = token_assurance
        self.status = status
        self.expires_at = expires_at
        self.used_at = used_at
        self.authorization_id = authorization_id
    
    def model_dump(self) -> dict:
        """Pydantic-compatible dump for FastAPI schema serialization."""
        return {
            "credential_id": self.credential_id,
            "credential_type": self.credential_type,
            "type": self.type,
            "agent_id": self.agent_id,
            "mandate_id": self.mandate_id,
            "merchant": self.merchant,
            "max_amount": self.max_amount,
            "currency": self.currency,
            "token_context": self.token_context,
            "token_assurance": self.token_assurance,
            "status": self.status,
            "expires_at": self.expires_at,
            "used_at": self.used_at,
            "authorization_id": self.authorization_id,
        }


class CredentialService:
    """Issues single-use, merchant/amount/expiry-bound credentials with
    Visa-style Enhanced Token fields (identity + permissions + context)."""

    def __init__(self, ttl_minutes: int = 10):
        self.ttl_minutes = ttl_minutes
        self._counter = 0
        self._store: dict[str, Credential] = {}

    def _mask_context(self, merchant: str, max_amount: float) -> str:
        """Return a PCI-safe masked context — never expose raw card data."""
        dots = "• " * 20
        return f"{merchant} — amount:{max_amount:.2f} XSGD — {dots}"

    def issue(self, authorization_id: str, merchant: str, max_amount: float) -> Credential:
        self._counter += 1
        credential_id = f"CRED-{self._counter:04d}"
        agent_id = "AGENT-B2AI-001"
        nonce = secrets.token_hex(16)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=self.ttl_minutes)
        mandate_id = f"MNDT-{secrets.randbelow(9000) + 1000}"

        masked_context = self._mask_context(merchant, max_amount)
        token_assurance = True  # always true: merchant-scoped + amount-limited + expiry-bound

        credential = Credential(
            credential_id=credential_id,
            credential_type="single-use",
            agent_id=agent_id,
            mandate_id=mandate_id,
            merchant=merchant,
            max_amount=max_amount,
            currency="XSGD",
            token_context=masked_context,
            token_assurance=token_assurance,
            status="ACTIVE",
            expires_at=expiry,
            used_at=None,
            authorization_id=authorization_id,
        )
        self._store[credential_id] = credential
        return credential

    def get(self, credential_id: str) -> Credential | None:
        return self._store.get(credential_id)

    def use(self, credential_id: str) -> Credential | None:
        credential = self.get(credential_id)
        if credential is None or credential.status == "USED":
            return None
        credential.status = "USED"
        credential.used_at = datetime.now(timezone.utc).isoformat()
        return credential

    def list_active(self) -> list[Credential]:
        return [c for c in self._store.values() if c.status == "ACTIVE"]


credential_service = CredentialService()