import type { AuthUser } from "../features/auth/authTypes";

export type ApiHealth = { status: "ok" | "degraded"; service: string; version: string };
export type LoginResult = { access_token: string; token_type: "bearer"; expires_at: string; user: AuthUser };
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
let authToken: string | null = null;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE) throw new Error("API base URL is not configured. Set VITE_API_BASE_URL in the frontend .env.local file.");
  const headers = new Headers(init?.headers || {});
  headers.set("Content-Type", "application/json");
  if (authToken) headers.set("Authorization", `Bearer ${authToken}`);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers, credentials: "omit" });
  if (response.status === 204) return undefined as T;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof body.detail === "string" ? body.detail : `API request failed (${response.status})`;
    throw new Error(detail);
  }
  return body as T;
}

export const api = {
  setAuthToken: (token: string | null) => { authToken = token; },
  login: (email: string, password: string) =>
    request<LoginResult>("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request<AuthUser>("/api/v1/auth/me"),
  logout: () => request<void>("/api/v1/auth/logout", { method: "POST" }),
  health: () => request<ApiHealth>("/api/v1/health"),
  demoOverview: () => request<Record<string, unknown>>("/api/v1/demo/overview"),
  demoMentors: () => request<Array<{ id: string; name: string; field: string; focus: string; institution: string }>>("/api/v1/demo/mentors"),
};
export const apiConfigured = Boolean(API_BASE);
