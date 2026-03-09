import streamlit as st
from fsd_generator import generate_fsd_orchestrator
from helpers import styled_card

def render_generation_page():
    st.markdown("## ⚙️ FSD Generation")
    
    brd_text = st.session_state.get("brd_text", "")
    if not brd_text:
        st.error("No BRD context found.")
        st.stop()
        
    verdict = st.session_state.get("verification_result", {}).get("verdict", "") if isinstance(st.session_state.get("verification_result"), dict) else ""
    
    if verdict == "FAIL":
        st.markdown(styled_card("error", "Warning: BRD Verification Failed", 
                    "You are generating from a BRD that failed quality checks. Ensure you've reviewed the issues."), 
                    unsafe_allow_html=True)
    elif verdict == "WARN":
         st.markdown(styled_card("warning", "Notice: BRD Verification Warned", 
                    "Generating from a BRD with known warnings."), 
                    unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Generator Control")
        if st.button("▶ Start Generation", type="primary", use_container_width=True):
            st.session_state["is_generating"] = True
            
        if st.session_state.get("fsd_sections", []):
            if st.button("View Output ➔", use_container_width=True):
                st.session_state["current_page"] = "Output"
                st.rerun()
                
        st.markdown("### Progress Log")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        log_container = st.container()
        
    with col2:
        st.markdown("### Live Preview")
        preview_area = st.empty()
        
        if not st.session_state.get("is_generating") and not st.session_state.get("fsd_sections"):
            preview_area.markdown("""
            <div class="glass-card" style="text-align: center; padding: 4rem;">
                <h3>Ready to Generate</h3>
                <p>Click 'Start Generation' to begin the AI orchestration process.</p>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.get("fsd_sections") and not st.session_state.get("is_generating"):
            preview_area.markdown("Generation complete. Navigate to Output page.")
            
    # Generation Logic
    if st.session_state.get("is_generating"):
        with st.spinner("Initializing AI Agents..."):
             generate_fsd_orchestrator(
                 brd_text,
                 st.session_state.get("project_meta", {}),
                 st.session_state.get("generation_settings", {}),
                 st.session_state.get("api_keys", {}),
                 progress_bar,
                 status_text,
                 preview_area
             )
        st.session_state["is_generating"] = False
        st.success("Generation successfully completed!")
        st.rerun()
