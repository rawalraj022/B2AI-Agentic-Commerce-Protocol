# B2AI Agentic Commerce Protocol

A **policy-controlled settlement layer** that lets AI agents spend self-custodied XSGD through existing payment rails, producing a verifiable link between the card authorization and the on-chain balance that funded it.

> **The LLM never touches funds.** Flow: `LLM → Agent → Structured Intent → Policy Engine → Payment Protocol`.

## Architecture

```
User
  ↓
AI Agent (OpenAI intent parsing)
  ↓
Structured Intent
  ↓
Discovery (mock catalog)
  ↓
Policy Engine (merchant / amount / currency / daily limit)
  ↓
XSGD Wallet (Avalanche Fuji C-Chain)
  ↓
Authorization (nonce + SHA-256 commitment)
  ↓
Single-use Payment Credential
  ↓
Mock Card Authorization
  ↓
XSGD Settlement (real ERC-20 transfer on Fuji)
  ↓
On-chain Receipt (Proof of Payment)
```

## Project Structure

```
B2AI-Agentic-Commerce-Protocol/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI + /purchase orchestration
│       ├── config.py            # env-driven settings
│       ├── database.py          # SQLAlchemy engine/session
│       ├── models.py            # wallets, policies, authorizations, credentials, payments
│       ├── schemas.py           # Pydantic models
│       ├── agent/               # OpenAI intent parser (+ mock fallback)
│       ├── discovery/           # mock product catalog
│       ├── policy/              # policy engine
│       ├── wallet/              # Web3.py Fuji + XSGD
│       ├── authorization/       # nonce + commitment
│       ├── issuance/            # single-use credential
│       ├── execution/           # mock card authorization
│       ├── settlement/          # real XSGD transfer on Fuji
│       └── receipt/             # proof-of-payment
├── contracts/
│   ├── AgentPaymentVault.sol    # authorize/settle/cancel with guards
│   ├── PaymentReceipt.sol       # on-chain receipt registry
│   └── interfaces/IERC20.sol
├── frontend/                    # React + Vite + Tailwind demo
├── tests/                       # pytest suite (15 tests)
├── docker-compose.yml
└── .env.example
```

## Quick Start (local)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your OpenAI key + Fuji RPC + XSGD address
uvicorn app.main:app --reload
```

> **macOS note:** if `web3` fails to build C extensions (`ckzg`/`lru-dict`), install with a single architecture:
> `ARCHFLAGS="-arch x86_64" pip install -r requirements.txt`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and type `Buy Nike running shoes for $40`, then click **Execute**.

### 3. Tests

```bash
cd backend && source venv/bin/activate
python -m pytest ../tests -v
```

### 4. Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/agent/intent` | Parse natural language into structured intent |
| POST | `/discovery/resolve` | Resolve product + merchant into a SKU |
| POST | `/policy/check` | Evaluate a transaction against policy |
| POST | `/authorization/create` | Create authorization with nonce + commitment |
| POST | `/credential/issue` | Issue a single-use credential |
| POST | `/payment/execute` | Execute payment against a credential |
| POST | `/settlement/settle` | Settle XSGD on-chain |
| POST | `/purchase` | **One-shot full pipeline** |
| GET | `/health` | Health check |

## Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `AGENT_PROVIDER` | `openai` or `mock` (rule-based fallback) |
| `OPENAI_API_KEY` | OpenAI key for intent parsing |
| `SIMULATE_SETTLEMENT` | `true` to never hit the chain (demo-safe) |
| `AVALANCHE_RPC_URL` | Fuji C-Chain RPC |
| `XSGD_CONTRACT_ADDRESS` | XSGD ERC-20 testnet address |
| `SETTLEMENT_PRIVATE_KEY` | Settlement key (never committed) |
| `DEFAULT_MAX_TRANSACTION` | Policy max per transaction |
| `DEFAULT_ALLOWED_MERCHANTS` | Comma-separated allowed merchants |

## Security Model

- **Self-custody:** the backend never holds the user's private key.
- **Policy guardrails:** the LLM cannot spend outside the configured policy.
- **Single-use credentials:** bound to merchant, amount, and expiry; `ACTIVE → USED`.
- **Commitment:** SHA-256 over `wallet + merchant + sku + amount + nonce + expiry` links the card authorization to the on-chain settlement.
- **Settlement fallback:** if the chain is unreachable, settlement degrades to a clearly-labeled simulated tx hash so the demo never breaks.

## Smart Contract Guards

`AgentPaymentVault.sol` enforces:
- ❌ no double-spend
- ❌ no amount > authorization
- ❌ no expired authorization
- ❌ no wrong merchant
- ❌ no reused credential
## Visa Trusted Agent Protocol — Architecture Mapping

| Visa TAP Concept | B2AI Implementation |
|------------------|---------------------|
| **AI Agent** (the shopper) | `backend/app/agent/agent.py` — parses user intent into structured `Intent` |
| **Agentic Commerce Protocol (ACP)** endpoints | `backend/app/main.py` (`/agent/intent`, `/discovery/resolve`, `/policy/check`) |
| **Merchant Agent Score** | `backend/app/directory/scorecard.py` → `GET /directory/merchants/{name}/score` |
| **Agent Trust Score** | `backend/app/directory/scorecard.py` → `GET /directory/agents/{id}/trust` |
| **Mandate** (signed payment instructions) | `backend/app/mandate/mandate.py` — EIP-712-like commitment over `(wallet, merchant, sku, amount, nonce, expiry)` |
| **Single-use Credentials / Tokens** | `backend/app/issuance/card.py` + `backend/app/authorization/authorization.py` — bound to merchant + amount + expiry; status `ACTIVE → USED` |
| **Human-in-the-loop Confirmation** | `backend/app/approval/approval.py` → `/purchase/request-confirmation` + `/purchase/confirm` |
| **Supervisor Agent (orchestrator)** | `backend/app/supervisor/agent.py` — invokes agents-as-tools: `parse_intent`, `resolve_discovery`, `evaluate_policy`, `create_authorization`, `issue_credential`, `execute_payment`, `settle` |
| **Multi-Rail Settlement** | `backend/app/rails/settlement.py` — `OnChainXSGD`, `MockCardRail`, `rail_router()` chooses by merchant preference |
| **Payment Receipt / Proof of Payment** | `backend/app/receipt/receipt.py` + `GET /receipt/{authorization_id}` — links card authorization to on-chain tx |
| **Smart Contract Vault** | `contracts/AgentPaymentVault.sol` — enforces all five guardrails (no double-spend, no amount > auth, no expiry, no wrong merchant, no reused credential) |

## End-to-End Flow (Supervisor Mode)

```
User ──► React UI ──► /supervisor/intent ──► SupervisorAgent
                                          │
                                          ├─► parse_intent (Agent)
                                          ├─► resolve_discovery (Directory)
                                          ├─► evaluate_policy (Policy)
                                          ├─► request_confirmation (Approval)
                                          ├─► create_authorization (Mandate)
                                          ├─► issue_credential (Token)
                                          ├─► execute_payment (Execution)
                                          └─► settle (Rail Router → XSGD / Card)
                                              └─► Receipt (Proof of Payment)
```

## Test Coverage (21 tests)

```
tests/test_authorization.py  — 3 tests  (commitment determinism)
tests/test_credential.py     — 4 tests  (single-use guarantees)
tests/test_policy.py         — 4 tests  (allow/deny rules)
tests/test_purchase.py       — 2 tests  (full pipeline orchestration)
tests/test_settlement.py     — 2 tests  (fallback to simulated)
tests/test_supervisor.py     — 6 tests  (rail router + supervisor orchestration)
```
