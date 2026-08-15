"""End-to-end /purchase pipeline tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_purchase_valid_flow():
    r = client.post("/purchase", json={"user_message": "Buy Nike running shoes for $40"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    steps = [s["step"] for s in data["timeline"]]
    assert "Intent" in steps
    assert "Discovery" in steps
    assert "Policy" in steps
    assert "Authorization" in steps
    assert "Credential" in steps
    assert "Execution" in steps
    assert "Settlement" in steps
    assert "Receipt" in steps
    assert data["receipt"]["status"] == "SETTLED"


def test_purchase_denied_for_unknown_merchant():
    r = client.post("/purchase", json={"user_message": "Buy a Ferrari for $40"})
    assert r.status_code == 200
    data = r.json()
    # Unknown merchant -> policy denies (or discovery fails), success is False
    assert data["success"] is False