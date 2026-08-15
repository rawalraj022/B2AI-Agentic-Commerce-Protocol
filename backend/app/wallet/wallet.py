"""Wallet module — connects to Avalanche Fuji C-Chain and reads XSGD balances.

The settlement private key lives in .env and is NEVER exposed via the API.
The user's wallet is self-custodied; the backend only reads balances and,
during settlement, signs the XSGD transfer with the configured key.
"""
from typing import Optional

from web3 import Web3

from ..config import settings

# Minimal ERC-20 ABI for balanceOf and transfer.
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]


class WalletService:
    """Reads XSGD balances and prepares settlement transactions on Fuji."""

    def __init__(self):
        self._w3 = None
        self._contract = None

    @property
    def w3(self):
        if self._w3 is None:
            self._w3 = Web3(Web3.HTTPProvider(settings.avalanche_rpc_url))
        return self._w3

    @property
    def contract(self):
        if self._contract is None:
            self._contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(settings.xsgd_contract_address),
                abi=ERC20_ABI,
            )
        return self._contract

    def is_connected(self) -> bool:
        try:
            return bool(self.w3.is_connected())
        except Exception:
            return False

    def get_decimals(self) -> int:
        try:
            return self.contract.functions.decimals().call()
        except Exception:
            return 6  # XSGD default

    def get_balance(self, address: str) -> float:
        """Return the XSGD balance (in whole units) for an address."""
        checksum = self.w3.to_checksum_address(address)
        decimals = self.get_decimals()
        raw = self.contract.functions.balanceOf(checksum).call()
        return raw / (10**decimals)

    def get_settlement_address(self) -> Optional[str]:
        """Derive the public address from the settlement private key."""
        if not settings.settlement_private_key:
            return None
        account = self.w3.eth.account.from_key(settings.settlement_private_key)
        return account.address


wallet = WalletService()