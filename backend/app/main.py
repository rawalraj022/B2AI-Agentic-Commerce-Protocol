"""FastAPI application for the B2AI Agentic Commerce Protocol."""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .agent.agent import agent
from .approval.approval import approval_service, approval_store
from .authorization.authorization import authorization_service
from .config import settings
from .database import get_db, init_db
from .directory.directory import directory as agentic_directory
from .directory.directory import scorecard
from .discovery.discovery import discovery
from .execution.executor import executor
from .issuance.card import credential_service
from .mandate.mandate import mandate_service
from .policy.policy_engine import policy_engine
from .receipt.receipt import receipt_service
from .schemas import (
    AuthorizationCreateRequest,
    AuthorizationOut,
    CredentialOut,
    ExecuteRequest,
    ExecutionResult,
    Intent,
    IntentRequest,
    Mandate,
    PolicyCheckRequest,
    PolicyDecision,
    Product,
    PurchaseProposal,
    PurchaseRequest,
    PurchaseResponse,
    Receipt,
    ResolveRequest,
    SettlementResult,
    SupervisorIntentRequest,
    TimelineStep,
)
from .settlement.settlement import settlement_service
from .supervisor.agent import supervisor as supervisor_agent
from .wallet.wallet import wallet
from .memory.agentcore_memory import memory

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


# --- Visa Agentic Directory (Phase 1) ---
@app.get("/directory/agents")
def list_agents() -> list[dict]:
    return [a.model_dump() for a in agentic_directory.list_agents()]


@app.get("/directory/merchants")
def list_merchants() -> list[dict]:
    return [m.model_dump() for m in agentic_directory.list_merchants()]


@app.get("/directory/agents/{agent_id}/trust")
def agent_trust(agent_id: str) -> dict:
    score = scorecard.agent_trust_score(agent_id)
    if score is None:
        raise HTTPException(status_code=404, detail="Agent not found in directory")
    return score


@app.get("/directory/merchants/{name}/score")
def merchant_score(name: str) -> dict:
    score = scorecard.merchant_agent_score(name)
    if score is None:
        raise HTTPException(status_code=404, detail="Merchant not found in directory")
    return score


# --- Mandate (Phase 2) ---
@app.post("/mandate/create", response_model=Mandate)
def create_mandate(
    user_wallet: str,
    agent_id: str,
    merchant: str,
    max_amount: float,
    currency: str = "XSGD",
) -> Mandate:
    return mandate_service.create(
        user_wallet=user_wallet,
        agent_id=agent_id,
        merchant=merchant,
        max_amount=max_amount,
        currency=currency,
    )


# --- Human-in-the-loop Approval (Phase 3) ---
@app.post("/purchase/request-confirmation", response_model=PurchaseProposal)
def request_confirmation(req: PurchaseProposal) -> PurchaseProposal:
    return approval_service.request_confirmation(
        merchant=req.merchant,
        amount=req.amount,
        currency=req.currency,
        mandate_id=req.mandate_id,
        agent_id=req.agent_id,
        sku=req.sku,
    )


@app.post("/purchase/confirm", response_model=PurchaseProposal)
def confirm_purchase(request_id: str) -> PurchaseProposal:
    try:
        return approval_service.confirm_purchase(request_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/purchase/decline", response_model=PurchaseProposal)
def decline_purchase(request_id: str) -> PurchaseProposal:
    try:
        return approval_service.decline_purchase(request_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/payment/approvals", response_model=list[PurchaseProposal])
def list_approvals() -> list[PurchaseProposal]:
    return approval_store.list_pending()


# --- Agent ---
@app.post("/agent/intent", response_model=Intent)
def understand_intent(req: IntentRequest) -> Intent:
    return agent.understand_intent(req.user_message)


# --- Discovery ---
@app.post("/discovery/resolve", response_model=Product)
def resolve_product(req: ResolveRequest) -> Product:
    product = discovery.resolve(req.product, req.merchant)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# --- Policy ---
@app.post("/policy/check", response_model=PolicyDecision)
def check_policy(req: PolicyCheckRequest) -> PolicyDecision:
    return policy_engine.authorize(req.merchant, req.amount, req.currency)


# --- Authorization ---
@app.post("/authorization/create", response_model=AuthorizationOut)
def create_authorization(req: AuthorizationCreateRequest) -> AuthorizationOut:
    return authorization_service.create(
        wallet_address=req.wallet_address,
        merchant=req.merchant,
        sku=req.sku,
        amount=req.amount,
        currency=req.currency,
    )


# --- Credential ---
@app.post("/credential/issue", response_model=CredentialOut)
def issue_credential(auth: AuthorizationOut) -> CredentialOut:
    return credential_service.issue(
        authorization_id=auth.authorization_id,
        merchant=auth.merchant,
        max_amount=auth.amount,
    )


# --- Execution ---
@app.post("/payment/execute", response_model=ExecutionResult)
def execute_payment(req: ExecuteRequest) -> ExecutionResult:
    return executor.execute(req.credential_id, req.merchant, req.amount)


# --- Settlement ---
@app.post("/settlement/settle", response_model=SettlementResult)
def settle_payment(to_address: str, amount: float) -> SettlementResult:
    return settlement_service.settle(to_address, amount)


# --- Receipt ---
@app.get("/receipt/{authorization_id}", response_model=Receipt)
def get_receipt(authorization_id: str) -> Receipt:
    raise HTTPException(status_code=404, detail="Receipt store not implemented; use /purchase")


# --- Supervisor Agent (Phase 5: agents-as-tools orchestration) ---
@app.post("/supervisor/intent")
def supervisor_intent(req: SupervisorIntentRequest) -> dict:
    return supervisor_agent.route_intent(
        req.user_message, wallet_address=req.wallet_address or ""
    )


# --- One-shot purchase pipeline ---
@app.post("/purchase", response_model=PurchaseResponse)
def purchase(req: PurchaseRequest, db: Session = Depends(get_db)) -> PurchaseResponse:
    timeline: list[TimelineStep] = []

    # 1. Intent
    intent = agent.understand_intent(req.user_message)
    timeline.append(
        TimelineStep(
            step="Intent",
            status="ok",
            detail=f"Understood: {intent.product} from {intent.merchant} for {intent.max_amount} {intent.currency}",
            data=intent.model_dump(),
        )
    )

    # 2. Discovery
    product = discovery.resolve(intent.product, intent.merchant)
    if product is None:
        timeline.append(
            TimelineStep(step="Discovery", status="denied", detail="No matching SKU found")
        )
        return PurchaseResponse(success=False, timeline=timeline)
    timeline.append(
        TimelineStep(
            step="Discovery",
            status="ok",
            detail=f"SKU {product.sku} found: {product.name} at {product.price} {product.currency}",
            data=product.model_dump(),
        )
    )

    # 3. Policy
    decision = policy_engine.authorize(product.merchant, product.price, product.currency)
    if not decision.approved:
        timeline.append(
            TimelineStep(step="Policy", status="denied", detail=decision.reason, data=decision.model_dump())
        )
        return PurchaseResponse(success=False, timeline=timeline)
    timeline.append(
        TimelineStep(
            step="Policy",
            status="ok",
            detail="Policy approved: merchant, amount, currency, daily limit",
            data=decision.model_dump(),
        )
    )

    # 4. Wallet / balance
    wallet_address = req.wallet_address or wallet.get_settlement_address() or "0x0000000000000000000000000000000000000000"
    balance = None
    try:
        balance = wallet.get_balance(wallet_address)
    except Exception:
        balance = None
    timeline.append(
        TimelineStep(
            step="Wallet",
            status="ok",
            detail=f"XSGD wallet {wallet_address[:10]}... balance={balance if balance is not None else 'n/a'}",
            data={"wallet_address": wallet_address, "balance": balance},
        )
    )

    # 5. Authorization
    auth = authorization_service.create(
        wallet_address=wallet_address,
        merchant=product.merchant,
        sku=product.sku,
        amount=product.price,
        currency=product.currency,
    )
    timeline.append(
        TimelineStep(
            step="Authorization",
            status="ok",
            detail=f"Authorization {auth.authorization_id} created with commitment {auth.commitment[:16]}...",
            data=auth.model_dump(),
        )
    )

    # 6. Credential
    credential = credential_service.issue(
        authorization_id=auth.authorization_id,
        merchant=product.merchant,
        max_amount=product.price,
    )
    timeline.append(
        TimelineStep(
            step="Credential",
            status="ok",
            detail=f"Single-use credential {credential.credential_id} issued, expires {credential.expires_at.isoformat()}",
            data=credential.model_dump(),
        )
    )

    # 7. Execution
    execution = executor.execute(credential.credential_id, product.merchant, product.price)
    if execution.status != "SUCCESS":
        timeline.append(
            TimelineStep(step="Execution", status="denied", detail=execution.reason or "Execution failed")
        )
        return PurchaseResponse(success=False, timeline=timeline)
    timeline.append(
        TimelineStep(step="Execution", status="ok", detail="Payment authorized against single-use credential")
    )

    # 8. Settlement
    settlement = settlement_service.settle(wallet_address, product.price, product.currency)
    timeline.append(
        TimelineStep(
            step="Settlement",
            status="ok",
            detail=f"{product.price} {product.currency} settled on {settlement.network}"
            + (" (simulated)" if settlement.simulated else ""),
            data=settlement.model_dump(),
        )
    )

    # 9. Receipt
    receipt = receipt_service.build(
        authorization_id=auth.authorization_id,
        credential_id=credential.credential_id,
        merchant=product.merchant,
        sku=product.sku,
        amount=product.price,
        currency=product.currency,
        wallet_address=wallet_address,
        commitment=auth.commitment,
        transaction_hash=settlement.transaction_hash,
        network=settlement.network,
        simulated=settlement.simulated,
    )
    timeline.append(
        TimelineStep(
            step="Receipt",
            status="ok",
            detail=f"Receipt generated: {receipt.authorization_id}",
            data=receipt.model_dump(),
        )
    )

    return PurchaseResponse(success=True, timeline=timeline, receipt=receipt)
