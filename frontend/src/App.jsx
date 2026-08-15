import { useState, useEffect } from "react";
import {
  runPurchase,
  runSupervisorIntent,
  checkHealth,
  getMerchantScore,
  listMerchants,
  listAgents,
} from "./services/api.js";

const SAMPLE = "Buy Nike running shoes for $40";

function StatusIcon({ status }) {
  if (status === "ok" || status === "success") {
    return (
      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </span>
    );
  }
  if (status === "denied") {
    return (
      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-rose-500/20 text-rose-400">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </span>
    );
  }
  return (
    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-600/30 text-slate-400">
      <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </span>
  );
}

function Timeline({ steps }) {
  if (!steps || !Array.isArray(steps) || steps.length === 0) return null;
  return (
    <div className="mt-6 space-y-3">
      {steps.map((step, i) => (
        <div
          key={i}
          className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4"
        >
          <StatusIcon status={step.status} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">{step.step}</span>
              <span className="text-xs text-slate-500">step {i + 1}</span>
            </div>
            <p className="mt-1 text-sm text-slate-400">{step.detail}</p>
            {step.data && (
              <pre className="mt-2 max-h-32 overflow-y-auto rounded border border-slate-800 bg-slate-950 p-2 text-xs text-slate-400">
                {JSON.stringify(step.data, (k, v) =>
                  typeof v === "bigint" ? v.toString() : v, 2)}
              </pre>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function ReceiptCard({ receipt }) {
  if (!receipt) return null;
  return (
    <div className="mt-6 rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-6">
      <div className="flex items-center gap-2 text-emerald-400">
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="text-lg font-bold">Proof of Payment</h3>
      </div>
      <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-slate-500">Authorization</dt>
          <dd className="font-mono text-slate-200">{receipt.authorization_id}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Credential</dt>
          <dd className="font-mono text-slate-200">{receipt.credential_id}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Merchant / SKU</dt>
          <dd className="text-slate-200">
            {receipt.merchant} · {receipt.sku}
          </dd>
        </div>
        <div>
          <dt className="text-slate-500">Amount</dt>
          <dd className="text-slate-200">
            {receipt.amount} {receipt.currency}
          </dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-slate-500">Commitment</dt>
          <dd className="break-all font-mono text-xs text-slate-300">{receipt.commitment}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-slate-500">Transaction Hash</dt>
          <dd className="break-all font-mono text-xs text-emerald-300">{receipt.transaction_hash}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-slate-500">Network</dt>
          <dd className="text-slate-200">
            {receipt.network}
            {receipt.simulated && (
              <span className="ml-2 rounded bg-amber-500/20 px-2 py-0.5 text-xs text-amber-300">
                simulated
              </span>
            )}
          </dd>
        </div>
      </dl>
    </div>
  );
}

function ScorePanel({ score, agentTrust, isLoading }) {
  if (!isLoading && (!score || !agentTrust)) return null;
  return (
    <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
      {score && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h4 className="mb-2 text-sm font-medium text-slate-400">Merchant Agent Score</h4>
          <div className="flex items-center gap-3">
            <div className="text-3xl font-bold text-brand">{score.agent_score.toFixed(0)}</div>
            <div className="flex-1">
              <div className="h-2 w-full rounded bg-slate-800">
                <div
                  className="h-2 rounded bg-brand"
                  style={{ width: `${score.agent_score}%` }}
                />
              </div>
            </div>
          </div>
          <div className="mt-2 flex flex-wrap gap-3 text-xs">
            <span className={score.token_ready ? "text-emerald-400" : "text-slate-500"}>
              Token-Ready: {score.token_ready ? "Yes" : "No"}
            </span>
            <span className={score.catalog_api ? "text-emerald-400" : "text-slate-500"}>
              Catalog API: {score.catalog_api ? "Yes" : "No"}
            </span>
            <span className={score.verified ? "text-emerald-400" : "text-slate-500"}>
              Verified: {score.verified ? "Yes" : "No"}
            </span>
            <span className="text-slate-400">Rail: {score.settlement_rail}</span>
          </div>
        </div>
      )}
      {agentTrust && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h4 className="mb-2 text-sm font-medium text-slate-400">Agent Trust Score</h4>
          <div className="flex items-center gap-3">
            <div className="text-3xl font-bold text-brand">{agentTrust.trust_score.toFixed(0)}</div>
            <div className="flex-1">
              <div className="h-2 w-full rounded bg-slate-800">
                <div
                  className="h-2 rounded bg-brand"
                  style={{ width: `${agentTrust.trust_score}%` }}
                />
              </div>
            </div>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Verified: {agentTrust.verified ? "Yes" : "No"} · Agent ID: {agentTrust.agent_id}
          </div>
          <div className="mt-1 flex flex-wrap gap-1 text-xs">
            {agentTrust.capabilities.map((cap) => (
              <span key={cap} className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-400">
                {cap}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TokenRailPanel({ timeline, receipt }) {
  /* Extract token context + rail info from the timeline data */
  const tokenStep = timeline?.find((s) => s.step === "Credential");
  const settlementStep = timeline?.find((s) => s.step === "Settlement");
  const authStep = timeline?.find((s) => s.step === "Authorization");

  if (!tokenStep && !settlementStep && !authStep) return null;

  return (
    <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
      {(tokenStep?.data || authStep?.data || receipt) && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h4 className="mb-2 text-sm font-medium text-slate-400">Token / Credential</h4>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Credential ID</span>
              <span className="font-mono text-slate-200">
                {tokenStep?.data?.credential_id || receipt?.credential_id || "—"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Credential Type</span>
              <span className="text-slate-200">
                {tokenStep?.data?.type || "single_use"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Token Assurance</span>
              <span className={tokenStep?.data?.token_assurance ? "text-emerald-400" : "text-slate-400"}>
                {tokenStep?.data?.token_assurance ? "Verified (merchant + amount + expiry bound)" : "None"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Merchant-Scoped</span>
              <span className="text-emerald-400">
                {tokenStep?.data?.merchant || receipt?.merchant}
              </span>
            </div>
            {tokenStep?.data?.expires_at && (
              <div className="flex justify-between">
                <span className="text-slate-500">Expires</span>
                <span className="text-slate-200">{tokenStep.data.expires_at}</span>
              </div>
            )}
          </div>
        </div>
      )}
      {(settlementStep?.data || receipt) && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h4 className="mb-2 text-sm font-medium text-slate-400">Payment Rail / Settlement</h4>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Rail</span>
              <span className="text-slate-200">
                {settlementStep?.data?.network || receipt?.network || "—"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Simulated</span>
              <span className={settlementStep?.data?.simulated ? "text-amber-400" : "text-emerald-400"}>
                {settlementStep?.data?.simulated ? "Yes (fallback)" : "No (on-chain)"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Commitment</span>
              <dd className="break-all font-mono text-xs text-slate-300">
                {receipt?.commitment?.slice(0, 20)}...
              </dd>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Amount</span>
              <span className="text-slate-200">
                {receipt?.amount} {receipt?.currency}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ApprovalModal({ proposal, onConfirm, onCancel }) {
  if (!proposal) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl">
        <h3 className="text-lg font-bold text-white">Confirm Purchase</h3>
        <div className="mt-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-400">Merchant</span>
            <span className="text-slate-200">{proposal.merchant}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">SKU</span>
            <span className="font-mono text-slate-200">{proposal.sku}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Amount</span>
            <span className="text-emerald-400">{proposal.amount} {proposal.currency}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Agent</span>
            <span className="text-slate-200">{proposal.agent_id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Status</span>
            <span className="text-amber-300">{proposal.status}</span>
          </div>
        </div>
        <div className="mt-6 flex gap-3">
          <button
            onClick={() => onConfirm(proposal.request_id)}
            className="flex-1 rounded-xl bg-emerald-600 py-2 font-semibold text-white transition hover:bg-emerald-500"
          >
            Approve
          </button>
          <button
            onClick={onCancel}
            className="flex-1 rounded-xl border border-slate-700 py-2 font-semibold text-slate-300 transition hover:bg-slate-800"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [message, setMessage] = useState(SAMPLE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [useSupervisor, setUseSupervisor] = useState(true);
  const [agentScores, setAgentScores] = useState(null);
  const [isLoadingScores, setIsLoadingScores] = useState(false);

  // Load directory scores on startup
  useEffect(() => {
    async function loadScores() {
      setIsLoadingScores(true);
      try {
        const [merchants, agents] = await Promise.all([listMerchants(), listAgents()]);
        const nikeScore = await getMerchantScore("Nike");
        const nikeAgent = agents.length > 0 ? agents[0] : null;
        const agentTrust = nikeAgent
          ? await import("./services/api.js").then((m) => m.getAgentTrust(nikeAgent.agent_id))
          : null;
        setAgentScores({ merchant: nikeScore, agent: agentTrust });
      } catch (e) {
        // non-fatal
      } finally {
        setIsLoadingScores(false);
      }
    }
    loadScores();
  }, []);

  async function handleExecute() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = useSupervisor
        ? await runSupervisorIntent(message)
        : await runPurchase(message);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/50">
        <div className="mx-auto max-w-4xl px-4 py-6">
          <h1 className="text-2xl font-bold text-white">
            B2AI <span className="text-brand">Agentic Commerce</span>
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Policy-controlled settlement layer for AI agents spending self-custodied XSGD
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8">
        {/* Controls */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <label className="text-sm font-medium text-slate-300">
            What should your agent buy?
          </label>
          <div className="mt-2 flex gap-2">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleExecute()}
              placeholder='e.g. "Buy Nike running shoes for $40"'
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 placeholder-slate-500 focus:border-brand focus:outline-none"
            />
            <button
              onClick={handleExecute}
              disabled={loading || !message.trim()}
              className="rounded-xl bg-brand px-6 py-3 font-semibold text-white transition hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Executing..." : "Execute"}
            </button>
          </div>
          <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useSupervisor}
                onChange={(e) => setUseSupervisor(e.target.checked)}
                className="h-3 w-3"
              />
              Supervisor orchestration (Visa agents-as-tools)
            </label>
          </div>
          <p className="mt-2 text-xs text-slate-500">
            Try: "Buy Nike running shoes for $40" · "Buy AirPods from Apple" · "Buy a Kindle from Amazon"
          </p>
        </div>

        {/* Score panels */}
        <ScorePanel
          score={agentScores?.merchant}
          agentTrust={agentScores?.agent}
          isLoading={isLoadingScores}
        />

        {/* Token / Rail panels from result */}
        {result && (
          <TokenRailPanel timeline={result.timeline} receipt={result.receipt} />
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-300">
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <>
            <div className="mt-6 flex items-center gap-2">
              <span
                className={`rounded-full px-3 py-1 text-sm font-semibold ${
                  result.success
                    ? "bg-emerald-500/20 text-emerald-300"
                    : "bg-rose-500/20 text-rose-300"
                }`}
              >
                {result.success ? "Payment completed" : "Payment denied"}
              </span>
            </div>
            <Timeline steps={result.timeline} />
            {result.receipt && <ReceiptCard receipt={result.receipt} />}
          </>
        )}
      </main>
    </div>
  );
}
