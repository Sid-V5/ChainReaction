const API_BASE = "http://localhost:8001";
export const WS_URL = "ws://localhost:8001/api/alerts/ws";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  return res.json();
}

export async function fetchGraph() {
  const res = await fetch(`${API_BASE}/api/graph`);
  return res.json();
}

export async function fetchRepositories() {
  const res = await fetch(`${API_BASE}/api/repos`);
  return res.json();
}

export async function scanRepository(url) {
  const res = await fetch(`${API_BASE}/api/repos/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to scan repository");
  }
  return res.json();
}

export async function queryBlastRadius(pkg, depth = 5) {
  const res = await fetch(`${API_BASE}/api/graph/blast-radius?package=${encodeURIComponent(pkg)}&depth=${depth}`);
  if (!res.ok) throw new Error("Blast radius query failed");
  return res.json();
}

export async function simulateBreakingChange(pkg) {
  const res = await fetch(`${API_BASE}/api/graph/simulate-breaking-change`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ package: pkg })
  });
  if (!res.ok) throw new Error("Simulation failed");
  return res.json();
}

export async function fetchEcosystemAnalytics() {
  const res = await fetch(`${API_BASE}/api/repos/analytics/ecosystem`);
  return res.json();
}

export async function fetchFacetAnalytics() {
  const res = await fetch(`${API_BASE}/api/repos/analytics/facet`);
  return res.json();
}

export async function fetchLeaderboard() {
  const res = await fetch(`${API_BASE}/api/alerts/leaderboard`);
  return res.json();
}

export async function triggerZeroDay() {
  const res = await fetch(`${API_BASE}/api/alerts/simulate-zero-day`, {
    method: "POST"
  });
  return res.json();
}

export async function reseedDatabase() {
  const res = await fetch(`${API_BASE}/api/repos/reseed`, {
    method: "POST"
  });
  return res.json();
}
