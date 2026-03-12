import React, { useMemo, useState } from "react";
import { InputPage } from "./pages/InputPage";
import { VerifyPage } from "./pages/VerifyPage";
import { SettingsPage } from "./pages/SettingsPage";
import { GenerationPage } from "./pages/GenerationPage";
import { OutputPage } from "./pages/OutputPage";

export type Provider = "Auto" | "Groq" | "OpenAI";

export type AppState = {
  projectMeta: { name: string; context: string; tech_stack: string };
  apiKeys: { groq: string; groq_model: string; openai: string; openai_model: string };
  provider: Provider;
  brdText: string;
  brdTextForAi: string;
  verifyResult: any | null;
  enrichedBrdText: string;
  fsd: { sections: { title: string; content: string }[]; evaluation: string } | null;
};

function loadState(): AppState {
  const raw = localStorage.getItem("specforge_state");
  if (raw) {
    try {
      return JSON.parse(raw) as AppState;
    } catch {
      // ignore
    }
  }
  return {
    projectMeta: { name: "", context: "", tech_stack: "" },
    apiKeys: { groq: "", groq_model: "llama-3.3-70b-versatile", openai: "", openai_model: "gpt-5.2" },
    provider: "Auto",
    brdText: "",
    brdTextForAi: "",
    verifyResult: null,
    enrichedBrdText: "",
    fsd: null,
  };
}

function saveState(state: AppState) {
  localStorage.setItem("specforge_state", JSON.stringify(state));
}

type Page = "Input" | "Verify" | "Generation" | "Output" | "Settings";

export function App() {
  const [page, setPage] = useState<Page>("Input");
  const [state, setState] = useState<AppState>(() => loadState());

  const set = (patch: Partial<AppState>) => {
    setState((prev) => {
      const next = { ...prev, ...patch };
      saveState(next);
      return next;
    });
  };

  const nav = useMemo(
    () => [
      { id: "Input" as const, label: "Input" },
      { id: "Verify" as const, label: "Verify" },
      { id: "Generation" as const, label: "Generate" },
      { id: "Output" as const, label: "Output" },
      { id: "Settings" as const, label: "Settings" },
    ],
    [],
  );

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">SpecForge</div>
        <div className="subbrand">BRD → FSD, faster & clearer</div>
        <div className="nav">
          {nav.map((n) => (
            <button
              key={n.id}
              className={page === n.id ? "active" : ""}
              onClick={() => setPage(n.id)}
            >
              {n.label}
            </button>
          ))}
        </div>
        <div style={{ marginTop: 18 }} className="card">
          <h2>Status</h2>
          <div className="row">
            <span className="pill">
              BRD:{" "}
              <span className={state.brdText.trim() ? "pill good" : "pill bad"}>
                {state.brdText.trim() ? "Loaded" : "Missing"}
              </span>
            </span>
          </div>
          <div style={{ marginTop: 10 }} className="row">
            <span className="pill">
              Verified:{" "}
              <span
                className={
                  state.verifyResult?.verdict === "PASS"
                    ? "pill good"
                    : state.verifyResult?.verdict === "WARN"
                      ? "pill warn"
                      : state.verifyResult?.verdict === "FAIL"
                        ? "pill bad"
                        : "pill"
                }
              >
                {state.verifyResult?.verdict ?? "—"}
              </span>
            </span>
          </div>
          <div style={{ marginTop: 10 }} className="row">
            <span className="pill">
              FSD:{" "}
              <span className={state.fsd ? "pill good" : "pill"}>
                {state.fsd ? "Generated" : "—"}
              </span>
            </span>
          </div>
          <div style={{ marginTop: 12 }} className="mono">
            API: <span>{(import.meta as any).env?.VITE_API_BASE ?? "http://localhost:8000"}</span>
          </div>
        </div>
      </aside>

      <main className="content">
        {page === "Input" && <InputPage state={state} set={set} go={(p) => setPage(p)} />}
        {page === "Verify" && <VerifyPage state={state} set={set} go={(p) => setPage(p)} />}
        {page === "Generation" && <GenerationPage state={state} set={set} go={(p) => setPage(p)} />}
        {page === "Output" && <OutputPage state={state} set={set} go={(p) => setPage(p)} />}
        {page === "Settings" && <SettingsPage state={state} set={set} />}
      </main>
    </div>
  );
}

