import streamlit as st
import os

# Set page config FIRST
st.set_page_config(
    page_title="SpecForge | BRD-to-FSD Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "main.css")
try:
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

from sidebar import render_sidebar
# Import pages (we will create these later, using try-except for now to not break the app)
try:
    from input_page import render_input_page
except ImportError:
    render_input_page = lambda: st.warning("Input page not implemented yet.")
try:
    from verify_page import render_verify_page
except ImportError:
    render_verify_page = lambda: st.warning("Verify page not implemented yet.")
try:
    from generation_page import render_generation_page
except ImportError:
    render_generation_page = lambda: st.warning("Generation page not implemented yet.")
try:
    from output_page import render_output_page
except ImportError:
    render_output_page = lambda: st.warning("Output page not implemented yet.")
try:
    from settings_page import render_settings_page
except ImportError:
    render_settings_page = lambda: st.warning("Settings page not implemented yet.")


def init_session_state():
    defaults = {
        "current_page": "Input",
        "brd_text": "",
        "project_meta": {"name": "", "context": "", "tech_stack": ""},
        "brd_verified": False,
        "verification_result": None,
        "fsd_sections": [],
        "modules": [],
        "selected_module_id": "",
        "brd_gap_questions": None,
        "brd_gap_answers": {},
        "module_gap_questions": {},
        "module_gap_answers": {},
        "auto_enrich_brd": True,
        "auto_enrich_iters": 2,
        "verification_guidance": {
            "missing_elements": "",
            "red_flags": "",
            "recommendations": "",
        },
        "api_keys": {
            "groq": "",
            "groq_model": "llama-3.3-70b-versatile",
            "openai": "",
            "openai_model": "gpt-4o-mini",
        },
        "debug_mode": False,
        "generation_settings": {
            "depth": "Standard",
            "examples": True,
            "terminology": "Standard FSD",
            "language": "English",
            "model_provider": "Auto"
        }
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main():
    init_session_state()
    render_sidebar()
    
    page = st.session_state["current_page"]
    
    if page == "Input":
        render_input_page()
    elif page == "Verify":
        render_verify_page()
    elif page == "Generation":
        render_generation_page()
    elif page == "Output":
        render_output_page()
    elif page == "Settings":
        render_settings_page()

if __name__ == "__main__":
    main()
