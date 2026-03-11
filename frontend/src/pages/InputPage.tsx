import React from "react";
import type { AppState } from "../App";

export function InputPage(props: {
  state: AppState;
  set: (patch: Partial<AppState>) => void;
  go: (page: any) => void;
}) {
  const { state, set, go } = props;
  return (
    <>
      <div className="page-title">
        <h1>BRD Input</h1>
        <span className="pill">Tip: paste BRD + any constraints</span>
      </div>
      <div className="grid">
        <div className="card">
          <h2>Project</h2>
          <div className="field">
            <label>Project name</label>
            <input
              value={state.projectMeta.name}
              onChange={(e) => set({ projectMeta: { ...state.projectMeta, name: e.target.value } })}
              placeholder="e.g., Merchant Onboarding Portal"
            />
          </div>
          <div className="field">
            <label>Context</label>
            <textarea
              value={state.projectMeta.context}
              onChange={(e) =>
                set({ projectMeta: { ...state.projectMeta, context: e.target.value } })
              }
              placeholder="Business context, users, constraints…"
            />
          </div>
          <div className="field">
            <label>Tech stack (optional)</label>
            <textarea
              value={state.projectMeta.tech_stack}
              onChange={(e) =>
                set({ projectMeta: { ...state.projectMeta, tech_stack: e.target.value } })
              }
              placeholder={"Frontend: React\nBackend: Django REST\nDB: Postgres\nCloud/Auth: …"}
            />
          </div>
          <div className="row">
            <button className="btn" onClick={() => go("Verify")}>
              Go to Verify →
            </button>
            <button className="btn secondary" onClick={() => set({ brdText: "", verifyResult: null })}>
              Clear
            </button>
          </div>
        </div>

        <div className="card">
          <h2>BRD Text</h2>
          <div className="field">
            <label>Paste BRD</label>
            <textarea
              value={state.brdText}
              onChange={(e) => set({ brdText: e.target.value, verifyResult: null })}
              placeholder="Paste your BRD here…"
              style={{ minHeight: 420 }}
            />
          </div>
          <div className="mono">We’ll compose a BRD-for-AI with tech stack + guidance on Verify.</div>
        </div>
      </div>
    </>
  );
}

