"""Tests for AgentCore-style memory system."""
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

import pytest

from backend.app.memory.agentcore_memory import AgentMemory
from backend.app.memory.schemas import Interaction

@pytest.fixture
def temp_memory():
    """Create a temporary memory file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name
    yield AgentMemory(file_path=temp_path)
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)

def test_remember_interaction(temp_memory):
    """Test that interactions are recorded and persisted."""
    interaction = Interaction(
        timestamp=datetime.utcnow(),
        user_id="user_1",
        user_message="Buy Nike shoes for $50",
        intent_product="Nike Shoes",
        intent_merchant="Nike",
        intent_amount=50.0,
        authorization_id="auth_123",
        credential_id="cred_456",
        settlement_tx="0xabc123",
        status="success",
        detail="Purchase completed",
    )
    temp_memory.remember_interaction("user_1", interaction)
    
    # Recall and verify
    recalled = temp_memory.recall_recent("user_1", limit=1)
    assert len(recalled) == 1
    assert recalled[0].user_id == "user_1"
    assert recalled[0].intent_amount == 50.0

def test_recall_recent_ordering(temp_memory):
    """Test that recent interactions are returned in reverse chronological order."""
    base_time = datetime.utcnow()
    for i in range(3):
        interaction = Interaction(
            timestamp=base_time + timedelta(hours=i),
            user_id="user_2",
            user_message=f"Purchase {i}",
            intent_product=f"Product {i}",
            intent_merchant="Nike",
            intent_amount=float(10 + i),
            status="success",
            detail=f"Purchase {i}",
        )
        temp_memory.remember_interaction("user_2", interaction)
    
    recalled = temp_memory.recall_recent("user_2", limit=3)
    assert len(recalled) == 3
    # Most recent first
    assert recalled[0].intent_amount == 12.0
    assert recalled[1].intent_amount == 11.0
    assert recalled[2].intent_amount == 10.0

def test_set_and_get_preferences(temp_memory):
    """Test preference learning and retrieval."""
    temp_memory.set_user_preference("user_3", "max_amount", "100", confidence=0.9)
    temp_memory.set_user_preference("user_3", "preferred_merchant", "Nike")
    
    prefs = temp_memory.get_user_preferences("user_3")
    assert prefs["max_amount"] == "100"
    assert prefs["preferred_merchant"] == "Nike"

def test_daily_spend_calculation(temp_memory):
    """Test daily spend aggregation for today only."""
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    
    # Add interaction for yesterday
    interaction_old = Interaction(
        timestamp=yesterday,
        user_id="user_4",
        user_message="Old purchase",
        intent_product="Product",
        intent_merchant="Nike",
        intent_amount=50.0,
        status="success",
        detail="Old",
    )
    temp_memory.remember_interaction("user_4", interaction_old)
    
    # Add interaction for today
    interaction_new = Interaction(
        timestamp=today,
        user_id="user_4",
        user_message="New purchase",
        intent_product="Product",
        intent_merchant="Nike",
        intent_amount=30.0,
        status="success",
        detail="New",
    )
    temp_memory.remember_interaction("user_4", interaction_new)
    
    # Daily spend should only count today's
    daily_spend = temp_memory.get_daily_spend("user_4")
    assert daily_spend == 30.0

def test_memory_persistence(temp_memory):
    """Test that memory survives reload from disk."""
    temp_memory.set_user_preference("user_5", "max_amount", "200")
    
    # Reload memory from the same file
    reloaded = AgentMemory(file_path=temp_memory.file_path)
    prefs = reloaded.get_user_preferences("user_5")
    assert prefs["max_amount"] == "200"

def test_empty_user_memory(temp_memory):
    """Test handling of users with no history."""
    recalled = temp_memory.recall_recent("nonexistent_user", limit=5)
    assert recalled == []
    
    prefs = temp_memory.get_user_preferences("nonexistent_user")
    assert prefs == {}
    
    daily_spend = temp_memory.get_daily_spend("nonexistent_user")
    assert daily_spend == 0.0