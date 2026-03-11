import json
import html
import streamlit as st


def render_verification_result(result):
    if not result:
        return

    verdict = result.get("verdict", "FAIL")
    panel_class = "verify-panel "
    if verdict == "WARN":
        panel_class += "warning"
    elif verdict == "FAIL":
        panel_class += "error"

    score = result.get("overall_score", 0)

    st.markdown(
        f"""
    <div class="{panel_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                Verdict: <span class="status-pill status-{verdict.lower()}">{verdict}</span>
            </h2>
            <div style="font-size: 2rem; font-weight: bold; color: {'#10B981' if score>=80 else '#F59E0B' if score>=50 else '#EF4444'};">
                {score}/100
            </div>
        </div>
        <p style="font-size: 1.1rem;">{result.get('summary', '')}</p>
        <div style="margin-top: 1rem;">
            <strong>Recommendation:</strong> 
            <span class="status-pill status-info">{result.get('proceed_recommendation', '')}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Dimension Analysis")
    cols = st.columns(len(result.get("dimensions", {})) if result.get("dimensions") else 1)

    if result.get("dimensions"):
        for idx, (dim, data) in enumerate(result["dimensions"].items()):
            with cols[idx]:
                status_color = (
                    "#10B981"
                    if data.get("score", 0) >= 80
                    else "#F59E0B"
                    if data.get("score", 0) >= 50
                    else "#EF4444"
                )
                st.markdown(
                    f"""
                 <div class="dimension-card">
                     <div class="dimension-header">
                         <span style="text-transform: capitalize;">{dim}</span>
                         <span style="color: {status_color};">{data.get('score', 0)}</span>
                     </div>
                     <span style="font-size: 0.8rem; color: #a0a0a0;">{data.get('status', '')}</span>
                     <p style="font-size: 0.9rem; margin: 0; margin-top: 0.5rem;">{data.get('detail', '')}</p>
                 </div>
                 """,
                    unsafe_allow_html=True,
                )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Present Elements")
        for item in result.get("present_elements", []):
            st.markdown(f"- ✅ {item}")
    with col2:
        st.markdown("### Missing Elements")
        for item in result.get("missing_elements", []):
            st.markdown(f"- ❌ {item}")

    st.markdown("### Red Flags")
    for flag in result.get("red_flags", []):
        issue = flag.get("issue", "")
        issue_html = html.escape(str(issue))
        st.markdown(
            f"""
        <div class="red-flag-card">
            <strong>{flag.get('impact', 'High')} Impact:</strong>
            <div style="white-space: pre-wrap; margin-top: 0.25rem;">{issue_html}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    debug_enabled = (
        st.session_state.get("debug_mode", False)
        or str(st.session_state.get("generation_settings", {}).get("debug_mode", "")).lower()
        == "true"
    )
    if debug_enabled and result.get("_debug"):
        with st.expander("Debug details (verification)"):
            st.code(json.dumps(result["_debug"], indent=2), language="json")

    st.markdown("### Recommendations")
    for rec in result.get("recommendations", []):
        st.markdown(
            f"""
        <div class="rec-card">
            {rec}
        </div>
        """,
            unsafe_allow_html=True,
        )

