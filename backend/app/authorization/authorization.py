"""Authorization module — creates a time-boxed, commitment-bound authorization.

Generates a cryptographic nonce and a SHA-256 commitment over
wallet + merchant + sku + amount + nonce + expiry. This commitment is the
verifiable link between the card authorization and the on-chain balance.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from ..schemas import AuthorizationOut


def create_commitment(data: dict) -> str:
    """SHA-256 commitment over the payment parameters."""
    raw = (
        str(data["wallet_address"])
        + str(data["merchant"])
        + str(data["sku"])
        + str(data["amount"])
        + str(data["nonce"])
        + str(data["expiry"])
    )
    return hashlib.sha256(raw.encode()).hexdigest()


class AuthorizationService:
    """Creates authorizations with nonce, commitment, and expiry."""

    def __init__(self, ttl_minutes: int = 10):
        self.ttl_minutes = ttl_minutes
        self._counter = 0

    def create(
        self,
        wallet_address: str,
        merchant: str,
        sku: str,
        amount: float,
        currency: str = "XSGD",
    ) -> AuthorizationOut:
        self._counter += 1
        authorization_id = f"AUTH-{self._counter:03d}"

        nonce = secrets.token_hex(32)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=self.ttl_minutes)

        commitment = create_commitment(
            {
                "wallet_address": wallet_address,
                "merchant": merchant,
                "sku": sku,
                "amount": amount,
                "nonce": nonce,
                "expiry": expiry.isoformat(),
            }
        )

        return AuthorizationOut(
            authorization_id=authorization_id,
            wallet_address=wallet_address,
            merchant=merchant,
            sku=sku,
            amount=amount,
            currency=currency,
            nonce=nonce,
            commitment=commitment,
            expires_at=expiry,
            status="AUTHORIZED",
        )


authorization_service = AuthorizationService()