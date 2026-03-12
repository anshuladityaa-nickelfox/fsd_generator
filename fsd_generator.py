import streamlit as st
import time
from prompt_engine import build_section_prompt, build_quality_eval_prompt, SYSTEM_PROMPT, FSD_SECTIONS
from llm_client import AutoClient, GroqClient, OpenAIClient
from fsd_validator import auto_fix_fsd

def determine_client(provider, keys):
    openai_model = (keys or {}).get("openai_model") or "gpt-5.2"
    groq_model = (keys or {}).get("groq_model") or "llama-3.3-70b-versatile"
    if provider == "Groq":
        if not (keys or {}).get("groq"):
            raise ValueError("Groq API key missing. Add it in Settings or switch provider.")
        return GroqClient(keys.get("groq"), model_name=groq_model)
    elif provider == "OpenAI":
        if not (keys or {}).get("openai"):
            raise ValueError("OpenAI API key missing. Add it in Settings or switch provider.")
        return OpenAIClient(keys.get("openai"), model_name=openai_model)
    else:
        return AutoClient(
            keys.get("groq"),
            keys.get("openai"),
            groq_model=groq_model,
            openai_model=openai_model,
        )

def generate_fsd_orchestrator(brd_text, project_meta, settings, api_keys, progress_bar, status_text, preview_area):
    client = determine_client(settings.get("model_provider", "Auto"), api_keys)
    
    st.session_state["fsd_sections"] = []
    st.session_state["fsd_validation"] = None
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
            
            previous_summary += f"- {section_name}\n"
            
        except Exception as e:
            st.error(f"Error generating {section_name}: {e}")
            break
            
        progress_bar.progress((idx + 1) / total_sections)
        time.sleep(0.5)
        
    # Quick quality eval (existing)
    status_text.text("Running quality evaluation...")
    full_fsd = "\n\n".join([sec["content"] for sec in st.session_state.get("fsd_sections", [])])
    eval_prompt = build_quality_eval_prompt(full_fsd)
    try:
        eval_result = client.generate(eval_prompt, SYSTEM_PROMPT)
        st.session_state["fsd_evaluation"] = eval_result
    except Exception as e:
        st.session_state["fsd_evaluation"] = f"Evaluation failed: {e}"

    # ── AUTO-FIX VALIDATION LAYER ──────────────────────────────────────────
    status_text.text("🛡️ Running AI validation + auto-fix…")
    provider = settings.get("model_provider", "Auto")
    try:
        validation_result = auto_fix_fsd(
            fsd_sections=st.session_state["fsd_sections"],
            brd_text=brd_text,
            project_meta=project_meta,
            settings=settings,
            provider=provider,
            api_keys=api_keys,
            max_rounds=3,
        )
        # Update sections with fixed content
        st.session_state["fsd_sections"] = validation_result["sections"]
        st.session_state["fsd_validation"] = validation_result
    except Exception as e:
        status_text.text(f"Validation failed: {e}")
        st.session_state["fsd_validation"] = {
            "final_status": "ERROR",
            "initial_status": "UNKNOWN",
            "rounds_taken": 0,
            "fix_log": [],
            "audit_detail": {},
            "_error": str(e),
        }
        
    status_text.text("Generation Complete!")
    return True

