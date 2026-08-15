"""Authorization and commitment tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.authorization.authorization import AuthorizationService, create_commitment


def test_authorization_created():
    svc = AuthorizationService()
    auth = svc.create("0xABC", "Nike", "NIKE-AIR-001", 40, "XSGD")
    assert auth.authorization_id.startswith("AUTH-")
    assert auth.status == "AUTHORIZED"
    assert len(auth.nonce) == 64  # 32 bytes hex
    assert len(auth.commitment) == 64  # sha256 hex


def test_commitment_is_deterministic():
    data = {
        "wallet_address": "0xABC",
        "merchant": "Nike",
        "sku": "NIKE-AIR-001",
        "amount": 40,
        "nonce": "abc",
        "expiry": "2026-01-01T00:00:00",
    }
    c1 = create_commitment(data)
    c2 = create_commitment(data)
    assert c1 == c2


def test_commitment_changes_with_amount():
    data = {
        "wallet_address": "0xABC",
        "merchant": "Nike",
        "sku": "NIKE-AIR-001",
        "amount": 40,
        "nonce": "abc",
        "expiry": "2026-01-01T00:00:00",
    }
    c1 = create_commitment(data)
    data["amount"] = 41
    c2 = create_commitment(data)
    assert c1 != c2