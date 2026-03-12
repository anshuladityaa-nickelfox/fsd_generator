import json
import logging
import traceback
import html
import streamlit as st
from prompt_engine import (
    build_brd_verification_prompt,
    build_brd_enrichment_prompt,
    build_brd_gap_questions_prompt,
    build_brd_enrichment_from_answers_prompt,
    build_module_extraction_prompt,
    build_module_gap_questions_prompt,
    BRD_VERIFIER_SYSTEM_PROMPT,
    BRD_ENRICHER_SYSTEM_PROMPT,
    BRD_QUESTION_SYSTEM_PROMPT,
    MODULE_EXTRACT_SYSTEM_PROMPT,
)
from llm_client import AutoClient, GroqClient, OpenAIClient

logger = logging.getLogger(__name__)

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

def _truncate(value, limit=4000):
    if value is None:
        return None
    text = str(value)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…(truncated)…"

def _strip_code_fences(text: str) -> str:
    s = (text or "").strip()
    if s.startswith("```"):
        # Remove first fence line: ``` or ```json
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        # Remove trailing fence if present
        s = s.strip()
        if s.endswith("```"):
            s = s[: -3].strip()
    return s.strip()

def _parse_json_lenient(text: str):
    s = _strip_code_fences(text)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Try extracting the first JSON object from any surrounding text.
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = s[start : end + 1].strip()
            return json.loads(candidate)
        raise

def _error_debug(provider_name, exc, **extra):
    debug = {
        "provider": provider_name,
        "exception_type": type(exc).__name__,
        "exception_message": _truncate(exc, 4000),
        "traceback": _truncate(traceback.format_exc(), 12000),
        "packages": _pkg_versions(),
    }

    # Common structured fields (best-effort, no hard deps on SDKs).
    for attr in ("status_code", "code", "error", "details", "response"):
        val = getattr(exc, attr, None)
        if val:
            debug[f"exception_{attr}"] = _truncate(val, 4000)

    for k, v in extra.items():
        if v is not None:
            debug[k] = _truncate(v, 12000) if isinstance(v, str) else v

    return debug

def _pkg_versions():
    versions = {}
    try:
        import sys

        versions["python_executable"] = sys.executable
        versions["python_version"] = sys.version
    except Exception:
        pass

    try:
        from importlib import metadata, util

        def dist_version(dist_name: str):
            try:
                return metadata.version(dist_name)
            except Exception:
                return None

        def module_path(module_name: str):
            try:
                spec = util.find_spec(module_name)
                return getattr(spec, "origin", None) if spec else None
            except Exception:
                return None

        for dist, module in (
            ("groq", "groq"),
            ("httpx", "httpx"),
            ("openai", "openai"),
        ):
            v = dist_version(dist)
            if v:
                versions[dist] = v
            p = module_path(module)
            if p:
                versions[f"{dist}_path"] = p
    except Exception:
        pass

    return versions

def _verify_once(brd_text, project_meta, provider_name, api_keys):
    if not brd_text or len(brd_text.strip()) < 50:
        return {
            "verdict": "FAIL",
            "overall_score": 0,
            "brd_type_detected": "Unknown",
            "is_valid_brd": False,
            "confidence": "High",
            "dimensions": {},
            "present_elements": [],
            "missing_elements": ["All document content"],
            "red_flags": [{"issue": "Document is empty or too short to be a valid BRD.", "impact": "Critical"}],
            "recommendations": ["Upload a valid, substantial Business Requirements Document."],
            "summary": "The provided text is insufficient for analysis.",
            "proceed_recommendation": "Do Not Proceed"
        }

    client = determine_client(provider_name, api_keys)
    prompt = build_brd_verification_prompt(brd_text, project_meta)
    response_text = client.generate(prompt, BRD_VERIFIER_SYSTEM_PROMPT)
    return _parse_json_lenient(response_text)


def _enrich_brd(brd_text, project_meta, provider_name, api_keys, missing_elements):
    client = determine_client(provider_name, api_keys)
    prompt = build_brd_enrichment_prompt(brd_text, project_meta, missing_elements)
    response_text = client.generate(prompt, BRD_ENRICHER_SYSTEM_PROMPT)
    return _parse_json_lenient(response_text)

def generate_gap_questions(brd_text, project_meta, provider_name, api_keys, verification_result):
    client = determine_client(provider_name, api_keys)
    prompt = build_brd_gap_questions_prompt(brd_text, project_meta, verification_result)
    response_text = client.generate(prompt, BRD_QUESTION_SYSTEM_PROMPT)
    return _parse_json_lenient(response_text)


def enrich_brd_from_answers(brd_text, project_meta, provider_name, api_keys, questions_json, answers_json):
    client = determine_client(provider_name, api_keys)
    prompt = build_brd_enrichment_from_answers_prompt(
        brd_text, project_meta, questions_json, answers_json
    )
    response_text = client.generate(prompt, BRD_ENRICHER_SYSTEM_PROMPT)
    return _parse_json_lenient(response_text)

def extract_modules(brd_text, project_meta, provider_name, api_keys):
    client = determine_client(provider_name, api_keys)
    prompt = build_module_extraction_prompt(brd_text, project_meta)
    response_text = client.generate(prompt, MODULE_EXTRACT_SYSTEM_PROMPT)
    return _parse_json_lenient(response_text)


def generate_module_gap_questions(
    brd_text, project_meta, provider_name, api_keys, verification_result, module
):
    client = determine_client(provider_name, api_keys)
    prompt = build_module_gap_questions_prompt(
        brd_text, project_meta, module=module, verification_result=verification_result
    )
    response_text = client.generate(prompt, BRD_QUESTION_SYSTEM_PROMPT)
    return _parse_json_lenient(response_text)


def verify_brd(brd_text, project_meta, provider_name, api_keys, auto_enrich=False, max_iters=2):
    try:
        working_text = brd_text
        enrich_steps = []

        iterations = max(1, int(max_iters or 1)) if auto_enrich else 1
        for _ in range(iterations):
            result = _verify_once(working_text, project_meta, provider_name, api_keys)

            if not auto_enrich or result.get("verdict") == "PASS":
                break

            missing = result.get("missing_elements") or []
            if not missing:
                break

            enrichment = _enrich_brd(
                working_text,
                project_meta,
                provider_name,
                api_keys,
                missing_elements=missing[:10],
            )
            addendum = (enrichment.get("addendum_markdown") or "").strip()
            if not addendum:
                break

            enrich_steps.append(enrichment)
            working_text = (
                working_text.rstrip()
                + "\n\n---\n\n# AI-Generated BRD Addendum (Assumptions)\n\n"
                + addendum
                + "\n"
            )

        if working_text != brd_text:
            result["enriched_brd_text"] = working_text
            result["_enrichment_steps"] = enrich_steps
        return result

    except json.JSONDecodeError as e:
        logger.exception("BRD verification JSON parse failed (provider=%s)", provider_name)
        return {
            "verdict": "WARN",
            "overall_score": 50,
            "brd_type_detected": "Unknown (Parse Error)",
            "is_valid_brd": True,
            "confidence": "Low",
            "dimensions": {},
            "present_elements": [],
            "missing_elements": [],
            "red_flags": [{"issue": "Failed to parse AI response into structured JSON.", "impact": "High"}],
            "recommendations": ["Try verifying again. The AI model returned an invalid format."],
            "summary": f"JSON Parse Error: {str(e)}",
            "proceed_recommendation": "Proceed with Caution",
            "_debug": _error_debug(
                provider_name,
                e,
                response_preview=_truncate(getattr(e, "doc", ""), 6000),
            ),
        }
    except Exception as e:
        logger.exception("BRD verification failed (provider=%s)", provider_name)
        return {
            "verdict": "FAIL",
            "overall_score": 0,
            "brd_type_detected": "Error",
            "is_valid_brd": False,
            "confidence": "High",
            "dimensions": {},
            "present_elements": [],
            "missing_elements": [],
            "red_flags": [{"issue": f"API Error: {str(e)}", "impact": "Critical"}],
            "recommendations": ["Check API Keys and network connection."],
            "summary": "An API error occurred during verification.",
            "proceed_recommendation": "Do Not Proceed",
            "_debug": _error_debug(provider_name, e),
        }

def render_verification_result(result):
    if not result:
        return
        
    verdict = result.get("verdict", "FAIL")
    panel_class = "verify-panel "
    if verdict == "WARN":
        panel_class += "warning"
    elif verdict == "FAIL":
        panel_class += "error"
        
    score = result.get("overall_score", 0)
    
    st.markdown(f"""
    <div class="{panel_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                Verdict: <span class="status-pill status-{verdict.lower()}">{verdict}</span>
            </h2>
            <div style="font-size: 2rem; font-weight: bold; color: {'#10B981' if score>=80 else '#F59E0B' if score>=50 else '#EF4444'};">
                {score}/100
            </div>
        </div>
        <p style="font-size: 1.1rem;">{result.get('summary', '')}</p>
        <div style="margin-top: 1rem;">
            <strong>Recommendation:</strong> 
            <span class="status-pill status-info">{result.get('proceed_recommendation', '')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Dimension Analysis")
    cols = st.columns(len(result.get("dimensions", {})) if result.get("dimensions") else 1)
    
    if result.get("dimensions"):
         for idx, (dim, data) in enumerate(result["dimensions"].items()):
             with cols[idx]:
                 status_color = "#10B981" if data.get('score', 0)>=80 else "#F59E0B" if data.get('score', 0)>=50 else "#EF4444"
                 st.markdown(f"""
                 <div class="dimension-card">
                     <div class="dimension-header">
                         <span style="text-transform: capitalize;">{dim}</span>
                         <span style="color: {status_color};">{data.get('score', 0)}</span>
                     </div>
                     <span style="font-size: 0.8rem; color: #a0a0a0;">{data.get('status', '')}</span>
                     <p style="font-size: 0.9rem; margin: 0; margin-top: 0.5rem;">{data.get('detail', '')}</p>
                 </div>
                 """, unsafe_allow_html=True)
                 
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Present Elements")
        for item in result.get("present_elements", []):
            st.markdown(f"- ✅ {item}")
    with col2:
        st.markdown("### Missing Elements")
        for item in result.get("missing_elements", []):
            st.markdown(f"- ❌ {item}")
            
    st.markdown("### Red Flags")
    for flag in result.get("red_flags", []):
        issue = flag.get("issue", "")
        issue_html = html.escape(str(issue))
        st.markdown(f"""
        <div class="red-flag-card">
            <strong>{flag.get('impact', 'High')} Impact:</strong>
            <div style="white-space: pre-wrap; margin-top: 0.25rem;">{issue_html}</div>
        </div>
        """, unsafe_allow_html=True)

    debug_enabled = (
        st.session_state.get("debug_mode", False)
        or str(st.session_state.get("generation_settings", {}).get("debug_mode", "")).lower() == "true"
    )
    if debug_enabled and result.get("_debug"):
        with st.expander("Debug details (verification)"):
            st.code(json.dumps(result["_debug"], indent=2), language="json")
        
    st.markdown("### Recommendations")
    for rec in result.get("recommendations", []):
        st.markdown(f"""
        <div class="rec-card">
            {rec}
        </div>
        """, unsafe_allow_html=True)
