"""Memory data schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Interaction(BaseModel):
    """A single agent interaction (purchase, query, etc.)."""
    timestamp: datetime
    user_id: str
    user_message: str
    intent_product: str
    intent_merchant: str
    intent_amount: float
    authorization_id: Optional[str] = None
    credential_id: Optional[str] = None
    settlement_tx: Optional[str] = None
    status: str  # "success" | "denied" | "error"
    detail: str


class UserPreference(BaseModel):
    """User-learned preference."""
    key: str  # e.g., "max_amount", "preferred_merchant"
    value: str
    learned_at: datetime
    confidence: float = 1.0  # 0.0 to 1.0


class MemorySnapshot(BaseModel):
    """Full memory state."""
    user_id: str
    interactions: list[Interaction]
    preferences: list[UserPreference]
    last_updated: datetime