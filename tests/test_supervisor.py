"""Tests for the supervisor agent orchestration (Phase 5 + Phase 6)."""
import pytest

from app.rails.settlement import OnChainXSGD, MockCardRail, rail_router
from app.schemas import SettlementResult


def test_rail_router_default_is_xsgd():
    """Auto mode defaults to on-chain XSGD rail."""
    rail = rail_router(select="auto", merchant="Nike")
    assert isinstance(rail, OnChainXSGD)


def test_rail_router_preferred_card_fallback():
    """When merchant prefers 'card', router returns MockCardRail."""
    rail = rail_router(select="preferred", merchant="Nike", preferred_rail="card")
    assert isinstance(rail, MockCardRail)


def test_rail_router_preferred_xsgd():
    """When merchant prefers 'xsgd', router returns OnChainXSGD."""
    rail = rail_router(select="preferred", merchant="Nike", preferred_rail="xsgd")
    assert isinstance(rail, OnChainXSGD)


def test_onchain_settle_simulated_without_rpc():
    """OnChainXSGD without RPC connection returns simulated result."""
    rail = OnChainXSGD(rpc_url="", private_key="")
    result = rail.settle("0x0000000000000000000000000000000000000000", 40.0, "XSGD")
    assert result.status == "success"
    assert result.simulated is True
    assert "simulated" in result.network.lower()


def test_mock_card_rail_returns_transaction_hash():
    """MockCardRail returns a simulated transaction hash."""
    rail = MockCardRail()
    result = rail.settle("0x0000000000000000000000000000000000000000", 25.0, "XSGD")
    assert result.status == "success"
    assert result.simulated is True
    assert result.transaction_hash is not None
    assert "Mock" in result.network


def test_settlement_result_schema_serializable():
    """SettlementResult should be serializable for the frontend timeline."""
    result = SettlementResult(
        status="SETTLED",
        transaction_hash="0xabc123",
        network="Avalanche Fuji C-Chain",
        simulated=True,
        reason="Test",
    )
    dumped = result.model_dump()
    assert dumped["status"] == "SETTLED"
    assert dumped["transaction_hash"] == "0xabc123"
    assert dumped["simulated"] is True
    assert dumped["network"] == "Avalanche Fuji C-Chain"
