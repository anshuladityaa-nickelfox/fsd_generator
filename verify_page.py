import streamlit as st
from helpers import get_word_count, get_char_count, styled_card
from brd_verifier import verify_brd, render_verification_result

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
    
    with col1:
        st.markdown("### Summary")
        st.markdown(f"""
        <div class="glass-card">
            <p><strong>Project:</strong> {st.session_state['project_meta'].get('name', 'N/A')}</p>
            <p><strong>Word Count:</strong> {get_word_count(brd_text):,}</p>
            <p><strong>Char Count:</strong> {get_char_count(brd_text):,}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Actions")
        if st.button("🔄 Run Verification", type="primary", use_container_width=True):
            with st.spinner("Analyzing BRD quality..."):
                provider = st.session_state["generation_settings"].get("model_provider", "Auto")
                api_keys = st.session_state.get("api_keys", {})
                
                try:
                    result = verify_brd(
                        brd_text, 
                        st.session_state.get("project_meta", {}),
                        provider,
                        api_keys
                    )
                    st.session_state["verification_result"] = result
                    st.session_state["brd_verified"] = True
                except Exception as e:
                    st.error(f"Failed to verify: {e}")
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
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <h3 style="color: #666;">No Verification Run Yet</h3>
                <p style="color: #888;">Click 'Run Verification' to analyze your document.</p>
            </div>
            """, unsafe_allow_html=True)
