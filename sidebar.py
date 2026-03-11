import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 class='gradient-text'>SpecForge</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #888;'>BRD-to-FSD Generator</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        
        pages = ["Input", "Verify", "Generation", "Output", "Settings"]
        
        for page in pages:
            # Custom styled button for active/inactive state
            is_active = st.session_state.get("current_page", "Input") == page
            
            button_style = "primary" if is_active else "secondary"
            if st.button(f"{page}", key=f"nav_{page}", use_container_width=True, type=button_style):
                st.session_state["current_page"] = page
                st.rerun()
                
        st.markdown("---")
        
        # Status Panel
        st.markdown("### Status")
        
        # 1. BRD Loaded
        brd_loaded = bool(st.session_state.get("brd_text", "").strip())
        if brd_loaded:
            st.markdown("- **BRD Loaded:** ✅")
        else:
            st.markdown("- **BRD Loaded:** ❌")
            
        # 2. BRD Verified
        brd_verified = st.session_state.get("brd_verified", False)
        verdict = st.session_state.get("verification_result", {}).get("verdict", "") if isinstance(st.session_state.get("verification_result"), dict) else ""
        
        if brd_verified and verdict:
            pill_class = {"PASS": "status-pass", "WARN": "status-warn", "FAIL": "status-fail"}.get(verdict, "status-info")
            st.markdown(f"- **BRD Verified:** <span class='status-pill {pill_class}'>{verdict}</span>", unsafe_allow_html=True)
        else:
            st.markdown("- **BRD Verified:** ❌")
            
        # 3. FSD Generated
        fsd_generated = bool(st.session_state.get("fsd_sections", []))
        if fsd_generated:
            st.markdown("- **FSD Generated:** ✅")
        else:
            st.markdown("- **FSD Generated:** ❌")

        st.markdown("---")
        st.caption("Powered by Groq & OpenAI")
