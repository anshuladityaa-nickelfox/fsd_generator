from prompt_engine import build_section_prompt, build_quality_eval_prompt, SYSTEM_PROMPT, FSD_SECTIONS
from llm_client import AutoClient, GroqClient, OpenAIClient


def determine_client(provider, keys):
    openai_model = (keys or {}).get("openai_model") or "gpt-4o-mini"
    groq_model = (keys or {}).get("groq_model") or "llama-3.3-70b-versatile"
    if provider == "Groq":
        if not (keys or {}).get("groq"):
            raise ValueError("Groq API key missing. Add it in Settings or switch provider.")
        return GroqClient(keys.get("groq"), model_name=groq_model)
    if provider == "OpenAI":
        if not (keys or {}).get("openai"):
            raise ValueError("OpenAI API key missing. Add it in Settings or switch provider.")
        return OpenAIClient(keys.get("openai"), model_name=openai_model)
    return AutoClient(
        keys.get("groq"),
        keys.get("openai"),
        groq_model=groq_model,
        openai_model=openai_model,
    )


def generate_fsd(brd_text, project_meta, settings, api_keys):
    client = determine_client(settings.get("model_provider", "Auto"), api_keys)
    sections = []
    previous_summary = ""

    for section_name in FSD_SECTIONS:
        prompt = build_section_prompt(section_name, brd_text, previous_summary, settings)
        content = client.generate(prompt, SYSTEM_PROMPT)
        sections.append({"title": section_name, "content": content})
        previous_summary += f"- {section_name}\n"

    full_fsd = "\n\n".join([sec["content"] for sec in sections])
    eval_prompt = build_quality_eval_prompt(full_fsd)
    evaluation = client.generate(eval_prompt, SYSTEM_PROMPT)
    return {"sections": sections, "evaluation": evaluation}

