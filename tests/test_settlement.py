"""Settlement tests (simulated mode)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import settings
from app.settlement.settlement import SettlementService


def test_settlement_simulated_when_no_rpc(monkeypatch):
    monkeypatch.setattr(settings, "avalanche_rpc_url", "")
    svc = SettlementService()
    result = svc.settle("0xABC", 40, "XSGD")
    assert result.status == "SETTLED"
    assert result.simulated is True
    assert result.transaction_hash.startswith("0x")


def test_settlement_simulated_when_flag(monkeypatch):
    monkeypatch.setattr(settings, "simulate_settlement", True)
    svc = SettlementService()
    result = svc.settle("0xABC", 40, "XSGD")
    assert result.status == "SETTLED"
    assert result.simulated is True