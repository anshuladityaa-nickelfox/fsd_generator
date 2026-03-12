import streamlit as st
import io
from docx_exporter import markdown_to_docx
from helpers import generate_clipboard_js, styled_card
from fsd_validator import auto_fix_fsd


def _status_badge(status: str) -> str:
    # Use standard colors and icons for qualitative status
    color = "#22c55e" if status == "CLEAN" else ("#f59e0b" if status == "NEEDS_FIX" else "#ef4444")
    icon = "✅" if status == "CLEAN" else ("⚠️" if status == "NEEDS_FIX" else "❗")
    label = f"{icon} {status}"
    return (
        f"<span style='background:{color};color:#fff;padding:4px 12px;"
        f"border-radius:20px;font-weight:700;font-size:1rem;'>{label}</span>"
    )


def _render_validation_tab(validation: dict):
    if not validation:
        st.info("Validation has not run yet. Generate an FSD to trigger the auto-fix validation layer.")
        return

    err = validation.get("_error")
    if err:
        st.error(f"Validation error: {err}")
        return

    initial = validation.get("initial_status", "UNKNOWN")
    final = validation.get("final_status", "UNKNOWN")
    rounds = validation.get("rounds_taken", 0)
    fix_log = validation.get("fix_log", [])
    audit = validation.get("audit_detail", {})

    # ── Status summary ───────────────────────────────────────────────────────
    st.markdown("### Audit Status")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"**Initial:** {_status_badge(initial)}", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"**Final:** {_status_badge(final)}", unsafe_allow_html=True)
    with col_c:
        st.metric("Fix Rounds", rounds)

    summary = audit.get("overall_summary", "")
    if summary:
        st.markdown(f"> {summary}")

    st.markdown("---")

    # ── Per-section table ────────────────────────────────────────────────────
    section_audits = audit.get("section_audits") or []
    if section_audits:
        st.markdown("### Section-by-Section Audit")
        for sa in section_audits:
            sec_status = sa.get("status", "CLEAN")
            sec_title = sa.get("section", "Unknown")
            issues = sa.get("issues") or []
            suggestions = sa.get("suggestions") or []

            status_icon = "✅" if sec_status == "CLEAN" else "⚠️"
            with st.expander(f"{status_icon} {sec_title}", expanded=sec_status != "CLEAN"):
                if issues:
                    st.markdown("**Issues identified:**")
                    for i in issues:
                        st.markdown(f"- ❌ {i}")
                if suggestions:
                    st.markdown("**Suggestions:**")
                    for s in suggestions:
                        st.markdown(f"- 💡 {s}")
                if not issues and not suggestions:
                    st.success("No issues found for this section.")
    else:
        st.warning("No per-section audit data available.")

    st.markdown("---")

    # ── Fix log ──────────────────────────────────────────────────────────────
    if fix_log:
        st.markdown("### Auto-Fix Log")
        for entry in fix_log:
            round_n = entry.get("round", "?")
            sec = entry.get("section", "Unknown section")
            err_msg = entry.get("error", "")
            if err_msg:
                st.markdown(f"- 🔴 **Round {round_n}** | `{sec}` — Fix failed: {err_msg}")
            else:
                st.markdown(f"- ✅ **Round {round_n}** | `{sec}` — Rewritten to address issues.")
    else:
        st.info("No sections needed auto-fixing (all were clean from the start).")

    st.markdown("---")

    # ── Re-run button ────────────────────────────────────────────────────────
    st.markdown("### Re-Run Auto-Fix")
    st.caption("Trigger another fix pass on the current FSD. Useful if you edited sections manually.")
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        rounds_max = st.slider("Max fix rounds", min_value=1, max_value=5, value=3, step=1, key="refix_rounds")
    with col_r2:
        if st.button("🔁 Re-Run Auto-Fix", type="primary", use_container_width=True):
            brd_text = st.session_state.get("brd_text_for_ai") or st.session_state.get("brd_text", "")
            project_meta = st.session_state.get("project_meta", {})
            settings = st.session_state.get("generation_settings", {})
            api_keys = st.session_state.get("api_keys", {})
            provider = settings.get("model_provider", "Auto")
            with st.spinner("🛡️ Running auto-fix validation…"):
                from fsd_validator import auto_fix_fsd
                result = auto_fix_fsd(
                    fsd_sections=st.session_state["fsd_sections"],
                    brd_text=brd_text,
                    project_meta=project_meta,
                    settings=settings,
                    provider=provider,
                    api_keys=api_keys,
                    max_rounds=rounds_max,
                )
            st.session_state["fsd_sections"] = result["sections"]
            st.session_state["fsd_validation"] = result
            st.success(f"Auto-fix complete! Final status: {result['final_status']}")
            st.rerun()


def render_output_page():
    st.markdown("## 📄 FSD Output")
    
    sections = st.session_state.get("fsd_sections", [])
    if not sections:
        st.warning("No FSD generated. Please run the generation process first.")
        if st.button("← Go to Generation"):
            st.session_state["current_page"] = "Generation"
            st.rerun()
        return

    full_markdown = "\n\n".join([f"## {s['title']}\n\n{s['content']}" for s in sections])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        tab_preview, tab_edit, tab_nav, tab_validate = st.tabs(
            ["👁️ Preview", "✏️ Edit Markdown", "🧭 Navigator", "🛡️ Validation"]
        )
        
        with tab_preview:
            st.markdown(f"<div class='glass-card' style='max-height: 800px; overflow-y: auto;'>\n{full_markdown}\n</div>", unsafe_allow_html=True)
            
        with tab_edit:
             edited_markdown = st.text_area("Edit FSD Content", value=full_markdown, height=800)
             if st.button("Save Edits"):
                  st.session_state["edited_fsd"] = edited_markdown
                  st.success("Edits saved locally to session state.")
                  
        with tab_nav:
            st.markdown("### Section Quick Nav")
            for idx, sec in enumerate(sections):
                  with st.expander(f"{idx+1}. {sec['title']}"):
                      st.write(sec['content'][:500] + "...")
                      if st.button(f"Regenerate Section {idx+1}", key=f"regen_{idx}"):
                           st.info(f"Regeneration for {sec['title']} not yet implemented in UI.")

        with tab_validate:
            _render_validation_tab(st.session_state.get("fsd_validation"))
                           
    with col2:
        st.markdown("### Export Options")
        
        # Word Export
        if st.button("Prepare .docx Download", use_container_width=True, type="primary"):
            with st.spinner("Generating document..."):
                md_content = st.session_state.get("edited_fsd", full_markdown)
                output_path = "Generated_FSD.docx"
                try:
                     markdown_to_docx(md_content, st.session_state.get("project_meta", {}), output_path)
                     with open(output_path, "rb") as file:
                          st.download_button(
                               label="Download .docx",
                               data=file,
                               file_name="Generated_FSD.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               use_container_width=True
                          )
                except Exception as e:
                     st.error(f"Docx export failed: {e}")
                     
        # Markdown Export
        st.download_button(
             label="Download .md",
             data=st.session_state.get("edited_fsd", full_markdown),
             file_name="Generated_FSD.md",
             mime="text/markdown",
             use_container_width=True
        )
        
        # Clipboard
        st.components.v1.html(generate_clipboard_js("copy-btn", st.session_state.get("edited_fsd", full_markdown)), height=60)
        
        st.markdown("---")

        # Quick status badge in sidebar panel
        validation = st.session_state.get("fsd_validation")
        if validation and not validation.get("_error"):
            final_status = validation.get("final_status", "UNKNOWN")
            st.markdown("### Validation Status")
            st.markdown(_status_badge(final_status), unsafe_allow_html=True)
            st.caption(f"Auto-fix ran {validation.get('rounds_taken', 0)} round(s).")

        st.markdown("### Quality Evaluation")
        eval_data = st.session_state.get("fsd_evaluation", "Evaluation pending.")
        if isinstance(eval_data, str):
             st.markdown(f"<div class='glass-card'><p style='font-size: 0.9rem;'>{eval_data}</p></div>", unsafe_allow_html=True)
        else:
             st.json(eval_data)
