import streamlit as st
import os

def render_settings_page():
    st.markdown("## ⚙️ Settings Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### API Keys")
        st.markdown("API keys are stored securely in your local environment session.")
        
        # Load from .env if present initially
        groq_val = st.session_state["api_keys"].get("groq", os.environ.get("GROQ_API_KEY", ""))
        gemini_val = st.session_state["api_keys"].get("gemini", os.environ.get("GEMINI_API_KEY", ""))
        
        groq_key = st.text_input("Groq API Key (Llama3)", type="password", value=groq_val)
        gemini_key = st.text_input("Gemini API Key (1.5 Flash)", type="password", value=gemini_val)
        
        if st.button("Save Keys"):
            st.session_state["api_keys"]["groq"] = groq_key
            st.session_state["api_keys"]["gemini"] = gemini_key
            # Also set in env so other modules can pick it up via os.environ if needed
            os.environ["GROQ_API_KEY"] = groq_key
            os.environ["GEMINI_API_KEY"] = gemini_key
            st.success("API keys saved for this session!")
            
        st.markdown("#### Connection Tests")
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            if st.button("Test Groq"):
                if st.session_state["api_keys"].get("groq"):
                    try:
                        from llm_client import GroqClient
                        client = GroqClient(st.session_state["api_keys"]["groq"])
                        res = client.generate("Respond with 'OK'", "You are a tester.")
                        st.markdown("<span class='status-pill status-pass'>Groq Connected</span>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Groq Test Failed: {e}")
                else:
                    st.warning("No Groq key provided.")
                    
        with tcol2:
            if st.button("Test Gemini"):
                if st.session_state["api_keys"].get("gemini"):
                    try:
                        from llm_client import GeminiClient
                        client = GeminiClient(st.session_state["api_keys"]["gemini"])
                        res = client.generate("Respond with 'OK'", "You are a tester.")
                        st.markdown("<span class='status-pill status-pass'>Gemini Connected</span>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Gemini Test Failed: {e}")
                else:
                    st.warning("No Gemini key provided.")
                    
    with col2:
        st.markdown("### Generation Settings")
        
        st.session_state["generation_settings"]["depth"] = st.select_slider(
            "Detail Depth", 
            options=["Brief", "Standard", "Comprehensive", "Exhaustive"],
            value=st.session_state["generation_settings"].get("depth", "Standard")
        )
        
        st.session_state["generation_settings"]["terminology"] = st.selectbox(
            "Terminology Preset",
            ["Standard FSD", "Agile Epic/Story", "Enterprise Architecture", "Lean Startup"],
            index=["Standard FSD", "Agile Epic/Story", "Enterprise Architecture", "Lean Startup"].index(st.session_state["generation_settings"].get("terminology", "Standard FSD"))
        )
        
        st.session_state["generation_settings"]["examples"] = st.toggle(
            "Include Code/Payload Examples", 
            value=st.session_state["generation_settings"].get("examples", True)
        )
        
        st.session_state["generation_settings"]["language"] = st.selectbox(
             "Output Language",
             ["English", "Spanish", "French", "German", "Japanese"],
             index=["English", "Spanish", "French", "German", "Japanese"].index(st.session_state["generation_settings"].get("language", "English"))
        )
        
        st.markdown("---")
        st.markdown("""
        ### About SpecForge
        SpecForge is a premium AI orchestration platform designed to translate unstructured Business Requirements Documents into heavily structured, execution-ready Functional Specification Documents.
        
        *Version 1.0.0 | Built with Streamlit, Groq, and Gemini*
        """)
