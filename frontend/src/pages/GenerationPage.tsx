import React, { useMemo, useState } from "react";
import type { AppState } from "../App";
import { api } from "../api";

export function GenerationPage(props: {
  state: AppState;
  set: (patch: Partial<AppState>) => void;
  go: (page: any) => void;
}) {
  const { state, set, go } = props;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const brdForAi = useMemo(() => {
    const base = state.enrichedBrdText.trim() ? state.enrichedBrdText : state.brdText;
    const t = state.projectMeta.tech_stack?.trim();
    let out = base.trimEnd();
    if (t) out += `\n\n## Tech Stack (User-provided)\n${t}\n`;
    return out + "\n";
  }, [state.brdText, state.enrichedBrdText, state.projectMeta.tech_stack]);

  const run = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await api.generateFsd({
        brd_text: brdForAi,
        project_meta: state.projectMeta,
        settings: { model_provider: state.provider, depth: "Standard", examples: true, terminology: "Standard FSD", language: "English" },
        api_keys: state.apiKeys,
      });
      set({ fsd: res });
      go("Output");
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="page-title">
        <h1>Generate FSD</h1>
        <span className="pill">Provider: {state.provider}</span>
      </div>
      <div className="grid">
        <div className="card">
          <h2>Controls</h2>
          <div className="mono">This generates all FSD sections sequentially (can take a few minutes).</div>
          <div style={{ marginTop: 12 }} className="row">
            <button className="btn" onClick={run} disabled={busy || !state.brdText.trim()}>
              {busy ? "Generating…" : "Start generation"}
            </button>
            <button className="btn secondary" onClick={() => go("Verify")}>
              Back to Verify
            </button>
          </div>
          {error && (
            <div style={{ marginTop: 12 }} className="mono">
              {error}
            </div>
          )}
        </div>
        <div className="card">
          <h2>Input Preview</h2>
          <div className="mono" style={{ whiteSpace: "pre-wrap", maxHeight: 520, overflow: "auto" }}>
            {brdForAi}
          </div>
        </div>
      </div>
    </>
  );
}

