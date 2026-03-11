import React, { useMemo, useState } from "react";
import type { AppState } from "../App";
import { api } from "../api";

function pillClass(verdict?: string): string {
  if (verdict === "PASS") return "pill good";
  if (verdict === "WARN") return "pill warn";
  if (verdict === "FAIL") return "pill bad";
  return "pill";
}

export function VerifyPage(props: {
  state: AppState;
  set: (patch: Partial<AppState>) => void;
  go: (page: any) => void;
}) {
  const { state, set, go } = props;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>("");
  const [autoEnrich, setAutoEnrich] = useState(true);
  const [iters, setIters] = useState(2);

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
      const res = await api.verify({
        brd_text: brdForAi,
        project_meta: state.projectMeta,
        provider: state.provider,
        api_keys: state.apiKeys,
        auto_enrich: autoEnrich,
        max_iters: iters,
      });
      set({
        brdTextForAi: brdForAi,
        verifyResult: res,
        enrichedBrdText: (res as any).enriched_brd_text ?? state.enrichedBrdText,
      });
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setBusy(false);
    }
  };

  const r = state.verifyResult as any;
  const verdict: string | undefined = r?.verdict as any;

  return (
    <>
      <div className="page-title">
        <h1>Verify BRD</h1>
        <span className={pillClass(verdict)}>Verdict: {verdict ?? "—"}</span>
      </div>

      <div className="split">
        <div className="card">
          <h2>Controls</h2>
          <div className="field">
            <label>Auto-fill missing items (AI)</label>
            <select value={autoEnrich ? "yes" : "no"} onChange={(e) => setAutoEnrich(e.target.value === "yes")}>
              <option value="yes">Enabled</option>
              <option value="no">Disabled</option>
            </select>
          </div>
          <div className="field">
            <label>Max iterations</label>
            <input type="number" min={1} max={3} value={iters} onChange={(e) => setIters(Number(e.target.value))} />
          </div>

          <div className="row">
            <button className="btn" onClick={run} disabled={busy || !state.brdText.trim()}>
              {busy ? "Running…" : "Run verification"}
            </button>
            <button className="btn secondary" onClick={() => go("Generation")} disabled={!state.brdText.trim()}>
              Generate FSD →
            </button>
          </div>

          {error && (
            <div style={{ marginTop: 12 }} className="card">
              <h2>Error</h2>
              <div className="mono" style={{ whiteSpace: "pre-wrap" }}>
                {error}
              </div>
            </div>
          )}

          <div style={{ marginTop: 12 }} className="card">
            <h2>BRD-for-AI Preview</h2>
            <div className="mono" style={{ whiteSpace: "pre-wrap", maxHeight: 240, overflow: "auto" }}>
              {brdForAi}
            </div>
          </div>

          {!!state.enrichedBrdText.trim() && (
            <div style={{ marginTop: 12 }} className="card">
              <h2>Enriched BRD</h2>
              <div className="mono" style={{ whiteSpace: "pre-wrap", maxHeight: 240, overflow: "auto" }}>
                {state.enrichedBrdText}
              </div>
              <div className="mono" style={{ marginTop: 8 }}>
                Tip: copy the enriched addendum back into your BRD if you want it persisted.
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <h2>Results</h2>
          {!r && <div className="mono">Run verification to see results.</div>}
          {r && (
            <>
              <div className="row" style={{ justifyContent: "space-between" }}>
                <span className={pillClass(verdict)}>Verdict: {verdict}</span>
                <span className="pill">Score: {r.overall_score ?? 0}/100</span>
              </div>
              <div style={{ marginTop: 10, color: "var(--muted)" }}>{r.summary}</div>

              <div style={{ marginTop: 14 }} className="grid">
                <div className="card">
                  <h2>Missing</h2>
                  <ul className="list">
                    {(r.missing_elements ?? []).map((x: string, i: number) => (
                      <li key={i}>{x}</li>
                    ))}
                  </ul>
                </div>
                <div className="card">
                  <h2>Red Flags</h2>
                  <ul className="list">
                    {(r.red_flags ?? []).map((x: any, i: number) => (
                      <li key={i}>
                        <span className="pill">{x.impact}</span> {x.issue}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div style={{ marginTop: 14 }} className="card">
                <h2>Recommendations</h2>
                <ul className="list">
                  {(r.recommendations ?? []).map((x: string, i: number) => (
                    <li key={i}>{x}</li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

