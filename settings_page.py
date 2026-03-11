import streamlit as st
import os
import sys
import platform
from importlib import metadata, util

def render_settings_page():
    st.markdown("## ⚙️ Settings Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### API Keys")
        st.markdown("API keys are stored securely in your local environment session.")
        
        # Load from .env if present initially
        groq_val = st.session_state["api_keys"].get("groq", os.environ.get("GROQ_API_KEY", ""))
        openai_val = st.session_state["api_keys"].get("openai", os.environ.get("OPENAI_API_KEY", ""))
        
        groq_key = st.text_input("Groq API Key", type="password", value=groq_val)
        groq_model = st.text_input(
            "Groq Model Name",
            value=st.session_state.get("api_keys", {}).get("groq_model", "llama-3.3-70b-versatile"),
            help="If you see a model decommissioned error, change this to a supported Groq model.",
        )
        openai_key = st.text_input("OpenAI API Key", type="password", value=openai_val)
        openai_model = st.text_input(
            "OpenAI Model Name",
            value=st.session_state.get("api_keys", {}).get("openai_model", "gpt-4o-mini"),
            help="Example: gpt-4o-mini. Use a model available to your account.",
        )
        
        if st.button("Save Keys"):
            st.session_state["api_keys"]["groq"] = groq_key
            st.session_state["api_keys"]["groq_model"] = groq_model.strip()
            st.session_state["api_keys"]["openai"] = openai_key
            st.session_state["api_keys"]["openai_model"] = openai_model.strip()
            # Also set in env so other modules can pick it up via os.environ if needed
            os.environ["GROQ_API_KEY"] = groq_key
            os.environ["GROQ_MODEL"] = groq_model.strip()
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["OPENAI_MODEL"] = openai_model.strip()
            st.success("API keys saved for this session!")
            
        st.markdown("#### Connection Tests")
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            if st.button("Test Groq"):
                if st.session_state["api_keys"].get("groq"):
                    try:
                        from llm_client import GroqClient
                        client = GroqClient(
                            st.session_state["api_keys"]["groq"],
                            model_name=st.session_state["api_keys"].get(
                                "groq_model", "llama-3.3-70b-versatile"
                            ),
                        )
                        res = client.generate("Respond with 'OK'", "You are a tester.")
                        st.markdown("<span class='status-pill status-pass'>Groq Connected</span>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Groq Test Failed: {e}")
                else:
                    st.warning("No Groq key provided.")
                    
        with tcol2:
            if st.button("Test OpenAI"):
                if st.session_state["api_keys"].get("openai"):
                    try:
                        from llm_client import OpenAIClient

                        client = OpenAIClient(
                            st.session_state["api_keys"]["openai"],
                            model_name=st.session_state["api_keys"].get("openai_model", "gpt-4o-mini"),
                        )
                        res = client.generate("Respond with 'OK'", "You are a tester.")
                        st.markdown("<span class='status-pill status-pass'>OpenAI Connected</span>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"OpenAI Test Failed: {e}")
                else:
                    st.warning("No OpenAI key provided.")

        with st.expander("Environment diagnostics"):
            st.write("Python:", sys.version)
            st.write("Executable:", sys.executable)
            st.write("Platform:", platform.platform())
            for dist, module in (
                ("groq", "groq"),
                ("httpx", "httpx"),
                ("openai", "openai"),
            ):
                try:
                    st.write(f"{dist}:", metadata.version(dist))
                except Exception:
                    st.write(f"{dist}:", "not installed")
                try:
                    spec = util.find_spec(module)
                    st.write(f"{dist} path:", getattr(spec, "origin", None) if spec else None)
                except Exception:
                    st.write(f"{dist} path:", "unknown")
                    
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

        st.session_state["debug_mode"] = st.toggle(
            "Show Debug Details",
            value=st.session_state.get("debug_mode", False),
            help="Shows detailed error information (tracebacks and API error payloads) on verification/generation pages.",
        )
        
        st.markdown("---")
        st.markdown("""
        ### About SpecForge
        SpecForge is a premium AI orchestration platform designed to translate unstructured Business Requirements Documents into heavily structured, execution-ready Functional Specification Documents.
        
        *Version 1.0.0 | Built with Streamlit, Groq, and OpenAI*
        """)
