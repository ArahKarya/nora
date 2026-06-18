// API client NORA — cookie auth (credentials: include).
// Base dari NEXT_PUBLIC_API_URL, default http://localhost:8010.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export interface User {
  id: string;
  email: string;
}

export interface Topic {
  id: string;
  slug: string;
  name: string;
  description: string;
  count: number;
}

interface TopicApi {
  id: string;
  slug: string;
  name: string;
  description: string;
  chunk_count?: number | null;
  count?: number | null;
}

export interface Source {
  spec: string;
  version: string;
  section: string;
  title: string;
  similarity: number;
  chunk_text: string;
}

export type Flag = "HIGH" | "MEDIUM" | "LOW";

export interface QueryResult {
  answer: string;
  confidence: number;
  flag: string | null;
  verifier_verdict: string;
  sources: Source[];
  query_id: string;
  session_id: string;
}

export interface SessionMeta {
  id: string;
  topic_id: string;
  title?: string;
  created_at?: string;
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    let msg = `Request gagal (${res.status})`;
    try {
      const data = await res.json();
      msg = data.detail || data.message || data.error || msg;
    } catch {
      /* non-json body */
    }
    throw new ApiError(res.status, msg);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---- Auth ----
export function register(email: string, password: string): Promise<User> {
  return request<User>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(
  email: string,
  password: string
): Promise<{ access_token: string; user: User }> {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function logout(): Promise<void> {
  return request<void>("/api/auth/logout", { method: "POST" });
}

export function me(): Promise<User> {
  return request<User>("/api/auth/me");
}

// ---- Topics ----
export async function getTopics(): Promise<Topic[]> {
  const r = await request<{ topics: TopicApi[] } | TopicApi[]>("/api/topics");
  const arr = Array.isArray(r) ? r : r.topics ?? [];
  return arr.map((t) => ({
    id: t.id,
    slug: t.slug,
    name: t.name,
    description: t.description,
    count: t.chunk_count ?? t.count ?? 0,
  }));
}

// ---- Query / Sessions ----
export function postQuery(payload: {
  topic_id: string;
  message: string;
  session_id?: string;
}): Promise<QueryResult> {
  return request<QueryResult>("/api/query", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getSessions(): Promise<SessionMeta[]> {
  const r = await request<{ sessions: SessionMeta[] } | SessionMeta[]>("/api/sessions");
  return Array.isArray(r) ? r : r.sessions ?? [];
}

export function getSession(id: string): Promise<SessionMeta> {
  return request<SessionMeta>(`/api/sessions/${id}`);
}

export { ApiError };
