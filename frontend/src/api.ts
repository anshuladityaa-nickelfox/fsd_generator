export type ApiKeys = {
  groq?: string;
  groq_model?: string;
  openai?: string;
  openai_model?: string;
};

export type ProjectMeta = {
  name?: string;
  context?: string;
  tech_stack?: string;
};

export type VerifyResult = Record<string, unknown>;

const API_BASE = (import.meta as any).env?.VITE_API_BASE ?? "http://localhost:8000";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return JSON.parse(text) as T;
}

export const api = {
  verify: (req: {
    brd_text: string;
    project_meta: ProjectMeta;
    provider: "Auto" | "Groq" | "OpenAI";
    api_keys: ApiKeys;
    auto_enrich: boolean;
    max_iters: number;
  }) => postJson<VerifyResult>("/api/verify", req),
  extractModules: (req: {
    brd_text: string;
    project_meta: ProjectMeta;
    provider: "Auto" | "Groq" | "OpenAI";
    api_keys: ApiKeys;
  }) => postJson<{ modules: any[] }>("/api/modules/extract", req),
  generateFsd: (req: {
    brd_text: string;
    project_meta: ProjectMeta;
    settings: Record<string, unknown>;
    api_keys: ApiKeys;
  }) =>
    postJson<{ sections: { title: string; content: string }[]; evaluation: string }>(
      "/api/fsd/generate",
      req,
    ),
};

