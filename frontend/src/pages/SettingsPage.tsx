import React from "react";
import type { AppState, Provider } from "../App";

export function SettingsPage(props: { state: AppState; set: (patch: Partial<AppState>) => void }) {
  const { state, set } = props;
  return (
    <>
      <div className="page-title">
        <h1>Settings</h1>
        <span className="pill">Stored in localStorage</span>
      </div>

      <div className="grid">
        <div className="card">
          <h2>Provider</h2>
          <div className="field">
            <label>Model provider</label>
            <select
              value={state.provider}
              onChange={(e) => set({ provider: e.target.value as Provider })}
            >
              <option value="Auto">Auto</option>
              <option value="Groq">Groq</option>
              <option value="OpenAI">OpenAI</option>
            </select>
          </div>
          <div className="mono">
            Tip: keep Auto, but ensure at least one key is set.
          </div>
        </div>

        <div className="card">
          <h2>API Keys</h2>
          <div className="field">
            <label>Groq API key</label>
            <input
              value={state.apiKeys.groq}
              onChange={(e) => set({ apiKeys: { ...state.apiKeys, groq: e.target.value } })}
              placeholder="gsk_…"
            />
          </div>
          <div className="field">
            <label>Groq model</label>
            <input
              value={state.apiKeys.groq_model}
              onChange={(e) => set({ apiKeys: { ...state.apiKeys, groq_model: e.target.value } })}
              placeholder="llama-3.3-70b-versatile"
            />
          </div>
          <div className="field">
            <label>OpenAI API key</label>
            <input
              value={state.apiKeys.openai}
              onChange={(e) => set({ apiKeys: { ...state.apiKeys, openai: e.target.value } })}
              placeholder="sk-…"
            />
          </div>
          <div className="field">
            <label>OpenAI model</label>
            <input
              value={state.apiKeys.openai_model}
              onChange={(e) => set({ apiKeys: { ...state.apiKeys, openai_model: e.target.value } })}
              placeholder="gpt-4o-mini"
            />
          </div>
        </div>
      </div>
    </>
  );
}

