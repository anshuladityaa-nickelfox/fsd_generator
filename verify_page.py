import streamlit as st
from helpers import get_word_count, get_char_count, styled_card
import json
from brd_core import (
    verify_brd,
    generate_gap_questions,
    generate_module_gap_questions,
    extract_modules,
    enrich_brd_from_answers,
)
from brd_verifier_ui import render_verification_result

def render_verify_page():
    st.markdown("## 🔍 BRD Verification")
    
    brd_text = st.session_state.get("brd_text", "")
    if not brd_text:
        st.warning("No BRD text loaded. Please go to the Input page and provide your document.")
        if st.button("← Go to Input"):
            st.session_state["current_page"] = "Input"
            st.rerun()
        return

    col1, col2 = st.columns([1, 2])

    def _compose_brd_for_ai(base_text: str) -> str:
        tech_stack = st.session_state.get("project_meta", {}).get("tech_stack", "").strip()
        guidance = st.session_state.get("verification_guidance", {}) or {}
        missing_txt = (guidance.get("missing_elements") or "").strip()
        red_flags_txt = (guidance.get("red_flags") or "").strip()
        recs_txt = (guidance.get("recommendations") or "").strip()

        out = base_text.rstrip()
        if tech_stack:
            out += "\n\n## Tech Stack (User-provided)\n" + tech_stack + "\n"
        if missing_txt or red_flags_txt or recs_txt:
            out += "\n\n## Verification Guidance (User-provided)\n"
            if missing_txt:
                out += "\n### Missing Elements\n" + missing_txt + "\n"
            if red_flags_txt:
                out += "\n### Red Flags\n" + red_flags_txt + "\n"
            if recs_txt:
                out += "\n### Recommendations\n" + recs_txt + "\n"
        return out + "\n"
    
    with col1:
        st.markdown("### Summary")
        st.markdown(f"""
        <div class="glass-card">
            <p><strong>Project:</strong> {st.session_state['project_meta'].get('name', 'N/A')}</p>
            <p><strong>Word Count:</strong> {get_word_count(brd_text):,}</p>
            <p><strong>Char Count:</strong> {get_char_count(brd_text):,}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Tech Stack (Optional)")
        st.session_state["project_meta"]["tech_stack"] = st.text_area(
            "Paste your intended tech stack (frontend/backend/db/cloud/auth/etc.).",
            value=st.session_state["project_meta"].get("tech_stack", ""),
            height=120,
        )

        st.markdown("### Paste Findings (Optional)")
        st.caption("Paste items from Missing Elements / Red Flags / Recommendations to guide FSD generation more accurately.")
        guidance = st.session_state.get("verification_guidance", {}) or {}
        guidance["missing_elements"] = st.text_area(
            "Missing Elements (paste)",
            value=guidance.get("missing_elements", ""),
            height=120,
        )
        guidance["red_flags"] = st.text_area(
            "Red Flags (paste)",
            value=guidance.get("red_flags", ""),
            height=120,
        )
        guidance["recommendations"] = st.text_area(
            "Recommendations (paste)",
            value=guidance.get("recommendations", ""),
            height=120,
        )
        st.session_state["verification_guidance"] = guidance
        
        st.markdown("### Actions")
        auto_enrich = st.toggle(
            "Auto-fill missing BRD items (AI)",
            value=st.session_state.get("auto_enrich_brd", True),
            help="Runs a short loop: verify → add AI BRD addendum for missing items → re-verify.",
        )
        st.session_state["auto_enrich_brd"] = auto_enrich
        max_iters = st.slider(
            "Auto-fill iterations",
            min_value=1,
            max_value=3,
            value=int(st.session_state.get("auto_enrich_iters", 2)),
        )
        st.session_state["auto_enrich_iters"] = max_iters

        if st.button("🔄 Run Verification", type="primary", use_container_width=True):
            with st.spinner("Analyzing BRD quality..."):
                provider = st.session_state["generation_settings"].get("model_provider", "Auto")
                api_keys = st.session_state.get("api_keys", {})
                brd_text_for_ai = _compose_brd_for_ai(brd_text)
                st.session_state["brd_text_for_ai"] = brd_text_for_ai
                
                try:
                    result = verify_brd(
                        brd_text_for_ai,
                        st.session_state.get("project_meta", {}),
                        provider,
                        api_keys,
                        auto_enrich=auto_enrich,
                        max_iters=max_iters,
                    )
                    st.session_state["verification_result"] = result
                    st.session_state["brd_verified"] = True
                    if isinstance(result, dict) and result.get("enriched_brd_text"):
                        st.session_state["brd_text_enriched"] = result.get("enriched_brd_text")
                except Exception as e:
                    st.error(f"Failed to verify: {e}")
            st.rerun()

        if st.session_state.get("brd_text_enriched"):
            with st.expander("AI-enriched BRD (preview)"):
                st.text_area(
                    "Enriched BRD Text",
                    value=st.session_state["brd_text_enriched"],
                    height=260,
                )
                if st.button("Apply enriched BRD", use_container_width=True):
                    st.session_state["brd_text"] = st.session_state["brd_text_enriched"]
                    st.session_state["brd_text_for_ai"] = _compose_brd_for_ai(st.session_state["brd_text"])
                    st.session_state["brd_verified"] = False
                    st.success("Enriched BRD applied. Please re-run verification.")
                    st.rerun()

        if st.session_state.get("brd_text_for_ai"):
            with st.expander("Modules (extract + edit)"):
                provider = st.session_state["generation_settings"].get("model_provider", "Auto")
                api_keys = st.session_state.get("api_keys", {})
                if st.button("Extract modules from BRD", use_container_width=True):
                    payload = extract_modules(
                        st.session_state["brd_text_for_ai"],
                        st.session_state.get("project_meta", {}),
                        provider,
                        api_keys,
                    )
                    modules = (payload or {}).get("modules") if isinstance(payload, dict) else None
                    st.session_state["modules"] = modules or []
                    if st.session_state["modules"] and not st.session_state.get("selected_module_id"):
                        st.session_state["selected_module_id"] = st.session_state["modules"][0].get("id", "")
                    st.rerun()

                modules = st.session_state.get("modules") or []
                if modules:
                    ids = [m.get("id", f"module-{i}") for i, m in enumerate(modules)]
                    selected = st.selectbox(
                        "Current module",
                        options=ids,
                        index=ids.index(st.session_state.get("selected_module_id")) if st.session_state.get("selected_module_id") in ids else 0,
                    )
                    st.session_state["selected_module_id"] = selected
                    for i, m in enumerate(modules):
                        if m.get("id") != selected:
                            continue
                        st.markdown("Edit selected module")
                        m["id"] = st.text_input("Module ID", value=m.get("id", ""), key=f"mod_id_{i}")
                        m["name"] = st.text_input("Module Name", value=m.get("name", ""), key=f"mod_name_{i}")
                        m["description"] = st.text_area("Description", value=m.get("description", ""), height=90, key=f"mod_desc_{i}")
                        m["primary_entities"] = st.text_input(
                            "Primary Entities (comma-separated)",
                            value=", ".join(m.get("primary_entities", []) or []),
                            key=f"mod_ent_{i}",
                        ).split(",")
                        m["primary_entities"] = [x.strip() for x in m["primary_entities"] if x.strip()]
                        m["key_user_actions"] = st.text_input(
                            "Key User Actions (comma-separated)",
                            value=", ".join(m.get("key_user_actions", []) or []),
                            key=f"mod_act_{i}",
                        ).split(",")
                        m["key_user_actions"] = [x.strip() for x in m["key_user_actions"] if x.strip()]
                        if st.button("Delete this module", use_container_width=True, key=f"del_mod_{i}"):
                            st.session_state["modules"] = [mm for mm in modules if mm is not m]
                            st.session_state["selected_module_id"] = (
                                st.session_state["modules"][0].get("id", "") if st.session_state["modules"] else ""
                            )
                            st.rerun()
                        break

                    if st.button("Add new module", use_container_width=True):
                        st.session_state["modules"].append(
                            {"id": f"module-{len(st.session_state['modules'])+1}", "name": "", "description": "", "primary_entities": [], "key_user_actions": []}
                        )
                        st.session_state["selected_module_id"] = st.session_state["modules"][-1]["id"]
                        st.rerun()
            
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("← Edit BRD", use_container_width=True):
                st.session_state["current_page"] = "Input"
                st.rerun()
        with col_b:
            if st.button("Generate FSD →", use_container_width=True):
                 st.session_state["current_page"] = "Generation"
                 st.rerun()

    with col2:
        st.markdown("### Verification Results")
        
        if st.session_state.get("brd_verified") and st.session_state.get("verification_result"):
            result = st.session_state["verification_result"]
            if result.get("verdict") == "FAIL":
                st.markdown(styled_card("error", "Action Required", 
                            "The BRD failed verification. Please address the red flags below before generating the FSD."), 
                            unsafe_allow_html=True)
            elif result.get("verdict") == "WARN":
                st.markdown(styled_card("warning", "Review Recommended", 
                            "The BRD has warnings. Generation may produce incomplete FSD sections."), 
                            unsafe_allow_html=True)
                            
            render_verification_result(result)

            # Interactive clarification loop (module-by-module in small batches)
            if result.get("verdict") in ("WARN", "FAIL"):
                with st.expander("Clarify missing details (Q&A loop)"):
                    provider = st.session_state["generation_settings"].get("model_provider", "Auto")
                    api_keys = st.session_state.get("api_keys", {})
                    brd_text_for_ai = st.session_state.get("brd_text_for_ai") or brd_text
                    project_meta = st.session_state.get("project_meta", {})
                    modules = st.session_state.get("modules") or []
                    selected_module_id = st.session_state.get("selected_module_id") or ""
                    module_obj = None
                    if modules and selected_module_id:
                        for m in modules:
                            if m.get("id") == selected_module_id:
                                module_obj = m
                                break

                    colq1, colq2 = st.columns(2)
                    with colq1:
                        if st.button("Generate global questions", use_container_width=True):
                            q_payload = generate_gap_questions(
                                brd_text_for_ai,
                                project_meta,
                                provider,
                                api_keys,
                                verification_result=result,
                            )
                            st.session_state["brd_gap_questions"] = q_payload
                            st.session_state["brd_gap_answers"] = {}
                            st.rerun()
                    with colq2:
                        if st.button("Generate module questions", use_container_width=True, disabled=not bool(module_obj)):
                            q_payload = generate_module_gap_questions(
                                brd_text_for_ai,
                                project_meta,
                                provider,
                                api_keys,
                                verification_result=result,
                                module=module_obj,
                            )
                            module_id = (q_payload or {}).get("module_id") or (module_obj or {}).get("id") or "unknown"
                            st.session_state.setdefault("module_gap_questions", {})[module_id] = q_payload
                            st.session_state.setdefault("module_gap_answers", {})[module_id] = {}
                            st.rerun()

                    # Prefer module-specific questions if available for selected module, else global.
                    q_payload = None
                    module_id = (module_obj or {}).get("id") if module_obj else None
                    if module_id:
                        q_payload = (st.session_state.get("module_gap_questions") or {}).get(module_id)
                    if not q_payload:
                        q_payload = st.session_state.get("brd_gap_questions")

                    questions = (q_payload or {}).get("questions") if isinstance(q_payload, dict) else None
                    if questions:
                        st.markdown("Answer the questions below, then generate an addendum.")
                        if module_id and (st.session_state.get("module_gap_questions") or {}).get(module_id):
                            answers = (st.session_state.get("module_gap_answers") or {}).get(module_id, {})
                        else:
                            answers = st.session_state.get("brd_gap_answers", {})
                        for q in questions:
                            qid = q.get("id")
                            qtype = q.get("type", "text")
                            label = q.get("question", qid)
                            help_text = q.get("help")
                            required = bool(q.get("required", False))
                            key = f"ans_{qid}"

                            if qtype == "single_select":
                                opts = q.get("options") or []
                                answers[qid] = st.selectbox(
                                    label + (" *" if required else ""),
                                    options=opts,
                                    index=opts.index(q.get("default")) if q.get("default") in opts else 0,
                                    help=help_text,
                                    key=key,
                                )
                            elif qtype == "multi_select":
                                opts = q.get("options") or []
                                defaults = q.get("default") or []
                                answers[qid] = st.multiselect(
                                    label + (" *" if required else ""),
                                    options=opts,
                                    default=[d for d in defaults if d in opts],
                                    help=help_text,
                                    key=key,
                                )
                            elif qtype == "boolean":
                                answers[qid] = st.toggle(
                                    label + (" *" if required else ""),
                                    value=bool(q.get("default", False)),
                                    help=help_text,
                                    key=key,
                                )
                            elif qtype == "number":
                                answers[qid] = st.number_input(
                                    label + (" *" if required else ""),
                                    value=float(q.get("default") or 0),
                                    help=help_text,
                                    key=key,
                                )
                            else:
                                answers[qid] = st.text_area(
                                    label + (" *" if required else ""),
                                    value=str(q.get("default") or ""),
                                    height=90,
                                    help=help_text,
                                    key=key,
                                )

                        if module_id and (st.session_state.get("module_gap_questions") or {}).get(module_id):
                            st.session_state.setdefault("module_gap_answers", {})[module_id] = answers
                        else:
                            st.session_state["brd_gap_answers"] = answers

                        if st.button("Generate BRD addendum from answers", type="primary", use_container_width=True):
                            questions_json = json.dumps(q_payload, ensure_ascii=False)
                            answers_json = json.dumps(answers, ensure_ascii=False)
                            enrichment = enrich_brd_from_answers(
                                brd_text_for_ai,
                                project_meta,
                                provider,
                                api_keys,
                                questions_json=questions_json,
                                answers_json=answers_json,
                            )
                            addendum = (enrichment.get("addendum_markdown") or "").strip()
                            if addendum:
                                enriched_text = (
                                    brd_text_for_ai.rstrip()
                                    + "\n\n---\n\n# AI-Generated BRD Addendum (From Q&A)\n\n"
                                    + addendum
                                    + "\n"
                                )
                                st.session_state["brd_text_enriched"] = enriched_text
                                st.success("Addendum generated. Review and apply it on the left panel.")
                                st.rerun()
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <h3 style="color: #666;">No Verification Run Yet</h3>
                <p style="color: #888;">Click 'Run Verification' to analyze your document.</p>
            </div>
            """, unsafe_allow_html=True)
