"""Agentic Directory — Visa-style trust layer for verified agents and merchants.

Implements:
  - Agentic Directory: verified AI agents with a trust score + capabilities.
  - Merchant Directory: verified merchants with an Agent Score (how easily
    AI agents can transact with them) and token-readiness.
"""
from typing import Optional

from pydantic import BaseModel


class AgentRecord(BaseModel):
    agent_id: str
    name: str
    capabilities: list[str]
    trust_score: float  # 0-100: quality/verification of the agent
    verified: bool


class MerchantRecord(BaseModel):
    merchant_id: str
    name: str
    agent_score: float  # 0-100: how easy for agents to transact
    token_ready: bool   # supports Visa-style merchant-scoped tokens
    catalog_api: bool   # exposes structured machine-readable product data
    response_format: bool  # returns structured JSON responses
    settlement_rail: str   # preferred rail: "xsgd" | "card" | "both"
    verified: bool = True


# Seed data for the demo (aligned with the mock catalog).
AGENTS: list[AgentRecord] = [
    AgentRecord(
        agent_id="AGENT-B2AI-001",
        name="B2AI Shopping Agent",
        capabilities=["intent_parsing", "discovery", "policy_eval", "payment_credential"],
        trust_score=95.0,
        verified=True,
    )
]

MERCHANTS: list[MerchantRecord] = [
    MerchantRecord(
        merchant_id="MERC-NIKE-001",
        name="Nike",
        agent_score=92.0,
        token_ready=True,
        catalog_api=True,
        response_format=True,
        settlement_rail="xsgd",
        verified=True,
    ),
    MerchantRecord(
        merchant_id="MERC-AMZ-001",
        name="Amazon",
        agent_score=88.0,
        token_ready=True,
        catalog_api=True,
        response_format=True,
        settlement_rail="xsgd",
        verified=True,
    ),
    MerchantRecord(
        merchant_id="MERC-APL-001",
        name="Apple",
        agent_score=90.0,
        token_ready=True,
        catalog_api=True,
        response_format=True,
        settlement_rail="xsgd",
        verified=True,
    ),
]


class AgenticDirectory:
    """Registry of verified agents and merchants with trust scores."""

    def __init__(self):
        self.agents: dict[str, AgentRecord] = {a.agent_id: a for a in AGENTS}
        self.merchants: dict[str, MerchantRecord] = {m.merchant_id: m for m in MERCHANTS}

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        return self.agents.get(agent_id)

    def get_merchant(self, name: str) -> Optional[MerchantRecord]:
        """Look up a merchant by display name (case-insensitive)."""
        name_lower = name.lower()
        for m in self.merchants.values():
            if m.name.lower() == name_lower:
                return m
        return None

    def is_agent_verified(self, agent_id: str) -> bool:
        rec = self.get_agent(agent_id)
        return rec is not None and rec.verified

    def is_merchant_token_ready(self, merchant: str) -> bool:
        rec = self.get_merchant(merchant)
        return rec is not None and rec.token_ready

    def list_agents(self) -> list[AgentRecord]:
        return list(self.agents.values())

    def list_merchants(self) -> list[MerchantRecord]:
        return list(self.merchants.values())


directory = AgenticDirectory()


class Scorecard:
    """Computes agent + merchant scores (Agentic Score / Agent Score)."""

    @staticmethod
    def merchant_agent_score(merchant: str) -> Optional[dict]:
        rec = directory.get_merchant(merchant)
        if rec is None:
            return None
        return {
            "merchant_id": rec.merchant_id,
            "name": rec.name,
            "agent_score": rec.agent_score,
            "token_ready": rec.token_ready,
            "catalog_api": rec.catalog_api,
            "response_format": rec.response_format,
            "settlement_rail": rec.settlement_rail,
            "verified": rec.verified,
        }

    @staticmethod
    def agent_trust_score(agent_id: str) -> Optional[dict]:
        rec = directory.get_agent(agent_id)
        if rec is None:
            return None
        return {
            "agent_id": rec.agent_id,
            "name": rec.name,
            "trust_score": rec.trust_score,
            "verified": rec.verified,
            "capabilities": rec.capabilities,
        }


scorecard = Scorecard()