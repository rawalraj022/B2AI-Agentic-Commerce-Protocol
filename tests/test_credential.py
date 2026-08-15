"""Credential issuance and execution tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.execution.executor import executor
from app.issuance.card import credential_service


def _issue_credential():
    return credential_service.issue("AUTH-TEST", "Nike", 40)


def test_credential_issued_active():
    cred = _issue_credential()
    assert cred.status == "ACTIVE"
    assert cred.type == "single_use"
    assert cred.merchant == "Nike"
    assert cred.max_amount == 40


def test_credential_reuse_denied():
    cred = _issue_credential()
    first = executor.execute(cred.credential_id, "Nike", 40)
    assert first.status == "SUCCESS"
    second = executor.execute(cred.credential_id, "Nike", 40)
    assert second.status == "FAILED"
    assert "used" in second.reason.lower()


def test_credential_wrong_merchant_denied():
    cred = _issue_credential()
    result = executor.execute(cred.credential_id, "Amazon", 40)
    assert result.status == "FAILED"
    assert "merchant" in result.reason.lower()


def test_credential_amount_exceeds_denied():
    cred = _issue_credential()
    result = executor.execute(cred.credential_id, "Nike", 100)
    assert result.status == "FAILED"
    assert "amount" in result.reason.lower()