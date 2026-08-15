"""Receipt module — assembles the verifiable Proof of Payment."""
from ..schemas import Receipt


class ReceiptService:
    """Builds a receipt linking the card authorization to the on-chain settlement."""

    def build(
        self,
        authorization_id: str,
        credential_id: str,
        merchant: str,
        sku: str,
        amount: float,
        currency: str,
        wallet_address: str,
        commitment: str,
        transaction_hash: str | None,
        network: str,
        simulated: bool = False,
    ) -> Receipt:
        return Receipt(
            authorization_id=authorization_id,
            credential_id=credential_id,
            merchant=merchant,
            sku=sku,
            amount=amount,
            currency=currency,
            wallet_address=wallet_address,
            commitment=commitment,
            transaction_hash=transaction_hash,
            network=network,
            status="SETTLED",
            simulated=simulated,
        )


receipt_service = ReceiptService()