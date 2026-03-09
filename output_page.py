import streamlit as st
import io
from docx_exporter import markdown_to_docx
from helpers import generate_clipboard_js, styled_card

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
        tab_preview, tab_edit, tab_nav = st.tabs(["👁️ Preview", "✏️ Edit Markdown", "🧭 Navigator"])
        
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
                           
    with col2:
        st.markdown("### Export Options")
        
        # Word Export
        if st.button("Prepare .docx Download", use_container_width=True, type="primary"):
            with st.spinner("Generating document..."):
                md_content = st.session_state.get("edited_fsd", full_markdown)
                # Ideally save to a BytesIO object for Streamlit download
                # We'll mock the path saving here for simplicity in a real environment
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
        st.markdown("### Quality Evaluation")
        eval_data = st.session_state.get("fsd_evaluation", "Evaluation pending.")
        if isinstance(eval_data, str):
             st.markdown(f"<div class='glass-card'><p style='font-size: 0.9rem;'>{eval_data}</p></div>", unsafe_allow_html=True)
        else:
             # If structured eval implemented
             st.json(eval_data)
