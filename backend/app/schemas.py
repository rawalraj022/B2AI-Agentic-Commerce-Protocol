"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Agent ---
class IntentRequest(BaseModel):
    user_message: str = Field(..., description="Natural language purchase request")


class Intent(BaseModel):
    action: str = "purchase"
    product: str
    merchant: str
    max_amount: float
    currency: str = "XSGD"


# --- Discovery ---
class ResolveRequest(BaseModel):
    product: str
    merchant: str


class Product(BaseModel):
    sku: str
    merchant: str
    name: str
    price: float
    currency: str = "XSGD"
    checkout_url: str


# --- Policy ---
class PolicyCheckRequest(BaseModel):
    merchant: str
    amount: float
    currency: str = "XSGD"


class PolicyDecision(BaseModel):
    approved: bool
    reason: str
    checks: list[dict] = []


# --- Authorization ---
class AuthorizationCreateRequest(BaseModel):
    wallet_address: str
    merchant: str
    sku: str
    amount: float
    currency: str = "XSGD"


class AuthorizationOut(BaseModel):
    authorization_id: str
    wallet_address: str
    merchant: str
    sku: str
    amount: float
    currency: str
    nonce: str
    commitment: str
    expires_at: datetime
    status: str


# --- Credential ---
class CredentialOut(BaseModel):
    credential_id: str
    type: str
    max_amount: float
    merchant: str
    expires_at: datetime
    status: str


# --- Execution ---
class ExecuteRequest(BaseModel):
    credential_id: str
    merchant: str
    amount: float


class ExecutionResult(BaseModel):
    status: str
    reason: Optional[str] = None


# --- Settlement ---
class SettlementResult(BaseModel):
    status: str
    transaction_hash: Optional[str] = None
    network: str
    simulated: bool = False
    reason: Optional[str] = None


# --- Receipt ---
class Receipt(BaseModel):
    authorization_id: str
    credential_id: str
    merchant: str
    sku: str
    amount: float
    currency: str
    wallet_address: str
    commitment: str
    transaction_hash: Optional[str] = None
    network: str
    status: str
    simulated: bool = False


# --- Mandate (Visa-style signed spend authorization) ---
class Mandate(BaseModel):
    mandate_id: str
    user_wallet: str
    agent_id: str
    merchant: str
    max_amount: float
    currency: str = "XSGD"
    expiry: datetime
    signature: str
    nonce: str
    status: str = "ACTIVE"


# --- Approval (human-in-the-loop) ---
class PurchaseProposal(BaseModel):
    request_id: str = ""
    merchant: str
    amount: float
    currency: str = "XSGD"
    mandate_id: str
    agent_id: str
    sku: str
    status: str = "pending"
    created_at: Optional[datetime] = None


# --- Purchase orchestration ---
class PurchaseRequest(BaseModel):
    user_message: str
    wallet_address: Optional[str] = None


class SupervisorIntentRequest(BaseModel):
    """Request for the supervisor orchestration pipeline."""
    user_message: str
    wallet_address: Optional[str] = None


class TimelineStep(BaseModel):
    step: str
    status: str  # ok | denied | error
    detail: str
    data: Optional[dict] = None


class PurchaseResponse(BaseModel):
    success: bool
    timeline: list[TimelineStep]
    receipt: Optional[Receipt] = None