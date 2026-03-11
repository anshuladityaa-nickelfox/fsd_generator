import streamlit as st
from file_parser import parse_file

def render_input_page():
    st.markdown("## 📄 BRD Input & Configuration")
    st.markdown("Upload your Business Requirements Document or paste the text directly below.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Document Content")
        
        tab1, tab2 = st.tabs(["📝 Text Paste", "📎 File Upload"])
        
        with tab1:
            brd_text = st.text_area("Paste BRD Content", value=st.session_state.get("brd_text", ""), height=400)
            if brd_text != st.session_state.get("brd_text", ""):
                st.session_state["brd_text"] = brd_text
                st.session_state["brd_verified"] = False
                
        with tab2:
            uploaded_file = st.file_uploader("Upload BRD (.docx, .pdf, .txt)", type=['docx', 'pdf', 'txt'])
            if uploaded_file is not None:
                if st.button("Parse File"):
                    with st.spinner("Extracting text..."):
                        parsed_text = parse_file(uploaded_file)
                        st.session_state["brd_text"] = parsed_text
                        st.session_state["brd_verified"] = False
                    st.success("File parsed successfully! Check the Text Paste tab.")
                    st.rerun()
                    
    with col2:
        st.markdown("### Project Metadata")
        st.session_state["project_meta"]["name"] = st.text_input("Project Name", value=st.session_state["project_meta"].get("name", ""))
        st.session_state["project_meta"]["context"] = st.text_area("Additional Context (Optional)", value=st.session_state["project_meta"].get("context", ""), height=100)
        
        st.markdown("### Configuration")
        providers = ["Auto", "Groq", "OpenAI"]
        current_provider = st.session_state["generation_settings"].get("model_provider", "Auto")
        if current_provider not in providers:
            current_provider = "Auto"

        st.session_state["generation_settings"]["model_provider"] = st.selectbox(
            "AI Model Provider",
            providers,
            index=providers.index(current_provider),
        )
        
        st.markdown("### Actions")
        
        # Action Buttons
        if st.button("Verify BRD First", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "Verify"
            st.rerun()
            
        verdict = st.session_state.get("verification_result", {}).get("verdict", "") if isinstance(st.session_state.get("verification_result"), dict) else ""
        
        if verdict == "FAIL":
            st.warning("⚠️ BRD Verification Failed. It is highly recommended to revise before generation.")
            
        if st.button("Generate FSD", use_container_width=True):
            st.session_state["current_page"] = "Generation"
            st.rerun()
