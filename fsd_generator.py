import streamlit as st
import time
from prompt_engine import build_section_prompt, build_quality_eval_prompt, SYSTEM_PROMPT, FSD_SECTIONS
from llm_client import AutoClient, GroqClient, GeminiClient

def determine_client(provider, keys):
    if provider == "Groq":
        return GroqClient(keys.get("groq"))
    elif provider == "Gemini":
        return GeminiClient(keys.get("gemini"))
    else:
        return AutoClient(keys.get("groq"), keys.get("gemini"))

def generate_fsd_orchestrator(brd_text, project_meta, settings, api_keys, progress_bar, status_text, preview_area):
    client = determine_client(settings.get("model_provider", "Auto"), api_keys)
    
    st.session_state["fsd_sections"] = []
    previous_summary = ""
    
    total_sections = len(FSD_SECTIONS)
    
    for idx, section_name in enumerate(FSD_SECTIONS):
        status_text.text(f"Generating ({idx+1}/{total_sections}): {section_name}")
        
        prompt = build_section_prompt(section_name, brd_text, previous_summary, settings)
        
        try:
            content = client.generate(prompt, SYSTEM_PROMPT)
            
            section_data = {
                "title": section_name,
                "content": content
            }
            st.session_state["fsd_sections"].append(section_data)
            
            # Show live preview
            preview_area.markdown(f"### {section_name}\n\n{content}")
            
            # Simple summarization strategy: append the latest title to the context
            # A more robust App would summarize actual content
            previous_summary += f"- {section_name}\n"
            
        except Exception as e:
            st.error(f"Error generating {section_name}: {e}")
            break
            
        progress_bar.progress((idx + 1) / total_sections)
        time.sleep(0.5) # Rate limit padding mostly
        
    status_text.text("Running self-evaluation...")
    # Concat FSD 
    full_fsd = "\n\n".join([sec["content"] for sec in st.session_state.get("fsd_sections", [])])
    
    eval_prompt = build_quality_eval_prompt(full_fsd)
    try:
        eval_result = client.generate(eval_prompt, SYSTEM_PROMPT)
        st.session_state["fsd_evaluation"] = eval_result
    except Exception as e:
        st.session_state["fsd_evaluation"] = f"Evaluation failed: {e}"
        
    status_text.text("Generation Complete!")
    return True
