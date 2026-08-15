"""Directory integration for supervisor agent — agent + merchant scoring.

Provides the supervisor with quick lookups into the Agentic Directory and
merchant scorecard data (Agent Score / Agentic Score from Visa's framework).
"""
from __future__ import annotations

from ..directory.directory import AgenticDirectory, Scorecard, AgentRecord, MerchantRecord


def get_directory() -> AgenticDirectory:
    """Return the global agentic directory instance."""
    from ..directory.directory import directory as _directory
    return _directory


def merchant_score(merchant: str) -> dict | None:
    """Return the merchant Agent Score card (Visa-style Agent Score)."""
    from ..directory.directory import scorecard as _scorecard
    return _scorecard.merchant_agent_score(merchant)


def agent_trust(agent_id: str) -> dict | None:
    """Return the agent trust score card (Visa-style Agentic Directory)."""
    from ..directory.directory import scorecard as _scorecard
    return _scorecard.agent_trust_score(agent_id)
