export type ApiHealth = {
  status: "ok" | "degraded";
  service: string;
  version: string;
};
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE)
    throw new Error(
      "API base URL is not configured; using demonstration data.",
    );
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    credentials: "omit",
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}
export const api = {
  health: () => request<ApiHealth>("/api/v1/health"),
  demoOverview: () => request<Record<string, unknown>>("/api/v1/demo/overview"),
  demoMentors: () =>
    request<
      Array<{
        id: string;
        name: string;
        field: string;
        focus: string;
        institution: string;
      }>
    >("/api/v1/demo/mentors"),
  // Intentionally no report-submission endpoint in the proposal demonstrator.
};
export const apiConfigured = Boolean(API_BASE);
