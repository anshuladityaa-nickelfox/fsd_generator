import React from "react";
import type { AppState } from "../App";

export function OutputPage(props: { state: AppState; set: (patch: Partial<AppState>) => void; go: (p: any) => void }) {
  const { state, go } = props;
  const fsd = state.fsd;
  return (
    <>
      <div className="page-title">
        <h1>Output</h1>
        <span className="pill">{fsd ? `${fsd.sections.length} sections` : "No output yet"}</span>
      </div>
      {!fsd && (
        <div className="card">
          <h2>Empty</h2>
          <div className="mono">Generate an FSD first.</div>
          <div style={{ marginTop: 12 }}>
            <button className="btn" onClick={() => go("Generation")}>
              Go to Generate →
            </button>
          </div>
        </div>
      )}
      {fsd && (
        <div className="card">
          <h2>FSD</h2>
          <div className="mono" style={{ marginBottom: 10 }}>
            Evaluation: {fsd.evaluation}
          </div>
          {fsd.sections.map((s, idx) => (
            <div key={idx} className="card" style={{ marginTop: 12 }}>
              <h2>{s.title}</h2>
              <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{s.content}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

