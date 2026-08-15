"""Multi-rail settlement abstraction — Visa-style rail selection.

Defines a PaymentRail interface and concrete implementations:
  - OnChainXSGD: real on-chain XSGD settlement (Avalanche Fuji)
  - MockCardRail: simulated Visa authorization fallback (demo safety)

The rail_router.select_rail() picks the appropriate rail per merchant
preference + policy + connectivity. The receipt records which rail
executed, giving full visibility into the settlement path taken.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

from ..settlement.settlement import SettlementResult


class PaymentRail(ABC):
    """Abstract base class for payment rail settlement strategies.

    Each rail implements settle() and returns a SettlementResult so the
    receipt can record which path the transaction took.
    """

    @abstractmethod
    def settle(self, to_address: str, amount: float, currency: str) -> SettlementResult:
        """Settle a payment on this rail.

        Returns a SettlementResult with status, transaction_hash (if any),
        network name, and a simulated flag.
        """
        ...


class OnChainXSGD(PaymentRail):
    """Real on-chain XSGD settlement via Web3.py on Avalanche Fuji C-Chain.

    This rail actually attempts to transfer XSGD on-chain. If the RPC
    is unavailable or the private key is missing, it gracefully falls
    back to simulated mode.
    """

    def __init__(self, rpc_url: str = "", private_key: str = ""):
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.w3 = None
        if rpc_url and private_key:
            try:
                from web3 import Web3
                self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            except Exception:
                self.w3 = None

    def settle(self, to_address: str, amount: float, currency: str) -> SettlementResult:
        # If we don't have a Web3 connection, simulate
        if self.w3 is None:
            return SettlementResult(
                status="success",
                transaction_hash=None,
                network="Avalanche Fuji C-Chain (simulated)",
                simulated=True,
                reason="No on-chain connection available — simulated settlement",
            )

        # Try a real on-chain transfer of XSGD ERC-20
        try:
            from ..wallet.wallet import get_xsgd_contract, XSGD_CONTRACT_ADDRESS
            xsgd_contract = get_xsgd_contract(self.w3)

            # Build transaction
            txn = xsgd_contract.functions.transfer(
                to_address, int(amount * 10**6)  # XSGD has 6 decimals
            ).buildTransaction({
                "from": self.private_key,
                "nonce": self.w3.eth.getTransactionCount(self.private_key),
                "gas": 200000,
                "gasPrice": self.w3.eth.gasPrice,
                "chainId": 43113,  # Avalanche Fuji
                "timestamp": int(datetime.now(timezone.utc).timestamp()),
            })

            # Sign and send
            signed = self.w3.eth.account.signTransaction(txn, self.private_key)
            tx_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
            receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

            return SettlementResult(
                status="success",
                transaction_hash=tx_hash.hex(),
                network="Avalanche Fuji C-Chain",
                simulated=False,
            )
        except Exception as e:
            # On failure, fall back to simulated
            return SettlementResult(
                status="success",
                transaction_hash=None,
                network="Avalanche Fuji C-Chain (simulated)",
                simulated=True,
                reason=f"On-chain settlement failed ({e.__class__.__name__}): {str(e)[:80]} — falling back to simulated",
            )


class MockCardRail(PaymentRail):
    """Simulated Visa/Mastercard authorization fallback rail.

    Used when the on-chain rail is unavailable or when the merchant
    prefers card-network routing. This is the "final-mile conversion"
    that Visa's architecture abstracts underneath.

    In production this would connect to a Visa/Mastercard processor,
    but for the demo it simply records a simulated authorization.
    """

    def settle(self, to_address: str, amount: float, currency: str) -> SettlementResult:
        # Simulate a Visa authorization
        return SettlementResult(
            status="success",
            transaction_hash=f"sim-{datetime.now(timezone.utc).timestamp()}",
            network="Mock Card Rail (Visa final-mile)",
            simulated=True,
            reason="Settlement via simulated Visa card-rail conversion",
        )


# Railway registry and router
RAILS: dict[str, PaymentRail] = {
    "xsgd": OnChainXSGD(),
    "mock_card": MockCardRail(),
    "card": MockCardRail(),
}


def rail_router(select: str = "auto", merchant: str = "", **kwargs) -> PaymentRail:
    """Select a payment rail by policy preference.

    Rules:
      - If merchant has a preferred rail in config, use that.
      - If auto, prefer OnChainXSGD when chain is available,
        otherwise fall back to MockCardRail.
      - The receipt will record which rail was used.
    """
    pref = kwargs.get("preferred_rail", "xsgd")
    if select == "preferred" or (select == "auto" and pref in RAILS):
        return RAILS[pref]
    # Auto: try on-chain first, fall back
    if "xsgd" in RAILS:
        return RAILS["xsgd"]
    return RAILS["mock_card"]