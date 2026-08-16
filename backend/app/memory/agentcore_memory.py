"""AgentCore-style persistent memory — file-backed in-memory store."""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import settings
from .schemas import Interaction, UserPreference, MemorySnapshot

class AgentMemory:
    """Persistent agent memory backed by a JSON file."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = Path(file_path or settings.memory_file_path)
        self.data: dict = self._load()

    def _load(self) -> dict:
        """Load memory from disk, or initialize empty."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        """Persist memory to disk."""
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception:
            pass  # Silent fail on write errors

    def remember_interaction(self, user_id: str, interaction: Interaction):
        """Record a single interaction."""
        if user_id not in self.data:
            self.data[user_id] = {"interactions": [], "preferences": []}
        self.data[user_id]["interactions"].append(interaction.model_dump(mode="json"))
        # Keep only last 50 interactions per user
        self.data[user_id]["interactions"] = self.data[user_id]["interactions"][-50:]
        self._save()

    def recall_recent(self, user_id: str, limit: int = 5) -> list[Interaction]:
        """Get the most recent N interactions for a user."""
        if user_id not in self.data:
            return []
        raw = self.data[user_id].get("interactions", [])
        interactions = [Interaction(**r) for r in raw[-limit:]]
        return list(reversed(interactions))  # Most recent first

    def set_user_preference(self, user_id: str, key: str, value: str, confidence: float = 1.0):
        """Learn a user preference."""
        if user_id not in self.data:
            self.data[user_id] = {"interactions": [], "preferences": []}
        
        # Check if preference already exists
        prefs = self.data[user_id]["preferences"]
        for pref in prefs:
            if pref.get("key") == key:
                pref["value"] = value
                pref["confidence"] = confidence
                pref["learned_at"] = datetime.utcnow().isoformat()
                self._save()
                return
        
        # New preference
        prefs.append({
            "key": key,
            "value": value,
            "learned_at": datetime.utcnow().isoformat(),
            "confidence": confidence,
        })
        self._save()

    def get_user_preferences(self, user_id: str) -> dict:
        """Get all user preferences as a dict."""
        if user_id not in self.data:
            return {}
        prefs = self.data[user_id].get("preferences", [])
        return {p["key"]: p["value"] for p in prefs}

    def get_daily_spend(self, user_id: str) -> float:
        """Aggregate total spend by user today."""
        if user_id not in self.data:
            return 0.0
        
        today = datetime.utcnow().date()
        interactions = self.data[user_id].get("interactions", [])
        total = 0.0
        for inter in interactions:
            if inter.get("status") == "success":
                try:
                    inter_date = datetime.fromisoformat(inter["timestamp"]).date()
                    if inter_date == today:
                        total += inter.get("intent_amount", 0.0)
                except Exception:
                    pass
        return total

    def get_snapshot(self, user_id: str) -> MemorySnapshot:
        """Get full memory state for a user."""
        if user_id not in self.data:
            return MemorySnapshot(
                user_id=user_id,
                interactions=[],
                preferences=[],
                last_updated=datetime.utcnow(),
            )
        
        raw = self.data[user_id]
        interactions = [Interaction(**r) for r in raw.get("interactions", [])]
        preferences = [UserPreference(**p) for p in raw.get("preferences", [])]
        
        return MemorySnapshot(
            user_id=user_id,
            interactions=interactions,
            preferences=preferences,
            last_updated=datetime.utcnow(),
        )

# Global instance
memory = AgentMemory()