"""Settlement module — transfers XSGD on Avalanche Fuji C-Chain.

Uses the settlement private key from .env to sign an ERC-20 transfer.
If the chain is unreachable or simulation is enabled, it degrades to a
clearly-labeled simulated transaction hash so the demo never breaks.
"""
import secrets

from ..config import settings
from ..schemas import SettlementResult
from ..wallet.wallet import wallet


class SettlementService:
    """Settles an authorized payment by transferring XSGD on-chain."""

    def settle(self, to_address: str, amount: float, currency: str = "XSGD") -> SettlementResult:
        # Simulation mode: never hit the chain.
        if settings.simulate_settlement or not settings.avalanche_rpc_url:
            return SettlementResult(
                status="SETTLED",
                transaction_hash="0x" + secrets.token_hex(32),
                network=settings.settlement_network,
                simulated=True,
            )

        try:
            if not wallet.is_connected():
                return self._simulated("Avalanche RPC unreachable")

            if not settings.settlement_private_key:
                return self._simulated("No settlement private key configured")

            account = wallet.w3.eth.account.from_key(settings.settlement_private_key)
            decimals = wallet.get_decimals()
            raw_amount = int(amount * (10**decimals))

            # Build and sign the transfer.
            nonce = wallet.w3.eth.get_transaction_count(account.address)
            tx = wallet.contract.functions.transfer(
                wallet.w3.to_checksum_address(to_address), raw_amount
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": nonce,
                    "chainId": settings.chain_id,
                }
            )
            signed = account.sign_transaction(tx)
            tx_hash = wallet.w3.eth.send_raw_transaction(signed.raw_transaction)

            return SettlementResult(
                status="SETTLED",
                transaction_hash=wallet.w3.to_hex(tx_hash),
                network=settings.settlement_network,
                simulated=False,
            )
        except Exception as exc:  # noqa: BLE001
            return self._simulated(f"Settlement error: {exc}")

    def _simulated(self, reason: str) -> SettlementResult:
        return SettlementResult(
            status="SETTLED",
            transaction_hash="0x" + secrets.token_hex(32),
            network=settings.settlement_network,
            simulated=True,
            reason=reason,
        )


settlement_service = SettlementService()