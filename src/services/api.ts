import type { AuthUser } from "../features/auth/authTypes";

export type ApiHealth = { status: "ok" | "degraded"; service: string; version: string };
export type LoginResult = { access_token: string; token_type: "bearer"; expires_at: string; user: AuthUser };
export type MentorProfile = {
  id: number; user_id: number; name: string; title: string; discipline: string;
  bio: string; expertise: string[]; institution_id: number; institution: string;
  accepting_requests: boolean;
};
export type MentorshipRequest = {
  id: number; mentor_profile_id: number; member_user_id: number; member_name: string;
  mentor_user_id: number; mentor_name: string; mentor_title: string; message: string;
  goals: string; status: string; mentor_response: string | null; created_at: string;
};
export type MentorshipConnection = {
  id: number; request_id: number; member_user_id: number; member_name: string;
  mentor_user_id: number; mentor_name: string; status: string; created_at: string;
};
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
  createDemoCase: (payload: { institution_id: number; scenario_code: string; anonymous: boolean; consent_to_referral: boolean }) =>
    request<{ case_ref: string; workflow_status: string; consent_status: string; synthetic: boolean; message: string }>("/api/v1/cases", { method: "POST", body: JSON.stringify(payload) }),
  supportServices: () => request<Array<{ id: number; category: string; title: string; description: string; contact_label: string | null }>>("/api/v1/support/services"),
  demoOverview: () => request<Record<string, unknown>>("/api/v1/demo/overview"),
  demoMentors: () => request<Array<{ id: string; name: string; field: string; focus: string; institution: string }>>("/api/v1/demo/mentors"),
  mentorshipMentors: (params = "") => request<MentorProfile[]>(`/api/v1/mentorship/mentors${params}`),
  mentorshipRequests: () => request<MentorshipRequest[]>("/api/v1/mentorship/requests"),
  mentorshipConnections: () => request<MentorshipConnection[]>("/api/v1/mentorship/connections"),
  createMentorshipRequest: (payload: { mentor_profile_id: number; message: string; goals: string }) =>
    request<MentorshipRequest>("/api/v1/mentorship/requests", { method: "POST", body: JSON.stringify(payload) }),
  decideMentorshipRequest: (id: number, decision: "accepted" | "declined", response: string) =>
    request<MentorshipRequest>(`/api/v1/mentorship/requests/${id}/decision`, { method: "POST", body: JSON.stringify({ decision, response }) }),
  cancelMentorshipRequest: (id: number) =>
    request<{ id: number; status: string }>(`/api/v1/mentorship/requests/${id}/cancel`, { method: "POST" }),
  communityDiscussions: (q="", category="") => request<CommunityDiscussion[]>(`/api/v1/community/discussions?q=${encodeURIComponent(q)}&category=${encodeURIComponent(category)}`),
  createDiscussion: (payload:{title:string;category:string;body:string}) => request<CommunityDiscussion>("/api/v1/community/discussions",{method:"POST",body:JSON.stringify(payload)}),
  updateDiscussion: (id:number,payload:{title?:string;category?:string;body?:string}) => request<CommunityDiscussion>(`/api/v1/community/discussions/${id}`,{method:"PATCH",body:JSON.stringify(payload)}),
  createCommunityReply: (id:number,body:string) => request<CommunityReply>(`/api/v1/community/discussions/${id}/replies`,{method:"POST",body:JSON.stringify({body})}),
  updateCommunityReply: (id:number,body:string) => request<{id:number;body:string;status:string}>(`/api/v1/community/replies/${id}`,{method:"PATCH",body:JSON.stringify({body})}),
  moderateDiscussion: (id:number,status:"open"|"locked"|"hidden") => request<{id:number;status:string}>(`/api/v1/community/discussions/${id}/moderation`,{method:"PATCH",body:JSON.stringify({status})}),
  moderateReply: (id:number,status:"open"|"locked"|"hidden") => request<{id:number;status:string}>(`/api/v1/community/replies/${id}/moderation`,{method:"PATCH",body:JSON.stringify({status})}),
};
export const apiConfigured = Boolean(API_BASE);

export type CommunityReply = { id:number; author_user_id:number; author_name:string; body:string; status:string; created_at:string };
export type CommunityDiscussion = { id:number; title:string; category:string; body:string; status:string; author_user_id:number; author_name:string; institution_id:number; institution_name:string; created_at:string; updated_at:string; reply_count:number; replies:CommunityReply[] };
