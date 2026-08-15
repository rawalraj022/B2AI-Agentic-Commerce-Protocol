import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export async function runPurchase(userMessage, walletAddress = "") {
  const { data } = await api.post("/purchase", {
    user_message: userMessage,
    wallet_address: walletAddress || null,
  });
  return data;
}

export async function runSupervisorIntent(userMessage, walletAddress = "") {
  const { data } = await api.post("/supervisor/intent", {
    user_message: userMessage,
    wallet_address: walletAddress || null,
  });
  return data;
}

export async function checkHealth() {
  const { data } = await api.get("/health");
  return data;
}

export async function getMerchantScore(merchant) {
  try {
    const { data } = await api.get(`/directory/merchants/${merchant}/score`);
    return data;
  } catch (e) {
    return null;
  }
}

export async function getAgentTrust(agentId) {
  try {
    const { data } = await api.get(`/directory/agents/${agentId}/trust`);
    return data;
  } catch (e) {
    return null;
  }
}

export async function requestConfirmation(proposal) {
  const { data } = await api.post("/purchase/request-confirmation", proposal);
  return data;
}

export async function confirmPurchase(requestId) {
  const { data } = await api.post("/purchase/confirm", null, {
    params: { request_id: requestId },
  });
  return data;
}

export async function listApprovals() {
  const { data } = await api.get("/payment/approvals");
  return data;
}

export async function listMerchants() {
  const { data } = await api.get("/directory/merchants");
  return data;
}

export async function listAgents() {
  const { data } = await api.get("/directory/agents");
  return data;
}
