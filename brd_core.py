import json
import logging
import traceback

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
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        s = s.strip()
        if s.endswith("```"):
            s = s[: -3].strip()
    return s.strip()


def parse_json_lenient(text: str):
    s = _strip_code_fences(text)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
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

        for dist, module in (("groq", "groq"), ("httpx", "httpx"), ("openai", "openai")):
            v = dist_version(dist)
            if v:
                versions[dist] = v
            p = module_path(module)
            if p:
                versions[f"{dist}_path"] = p
    except Exception:
        pass
    return versions


def verify_brd(brd_text, project_meta, provider_name, api_keys, auto_enrich=False, max_iters=2):
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
            "red_flags": [
                {"issue": "Document is empty or too short to be a valid BRD.", "impact": "Critical"}
            ],
            "recommendations": ["Upload a valid, substantial Business Requirements Document."],
            "summary": "The provided text is insufficient for analysis.",
            "proceed_recommendation": "Do Not Proceed",
        }

    try:
        working_text = brd_text
        enrich_steps = []

        iterations = max(1, int(max_iters or 1)) if auto_enrich else 1
        for _ in range(iterations):
            client = determine_client(provider_name, api_keys)
            prompt = build_brd_verification_prompt(working_text, project_meta)
            response_text = client.generate(prompt, BRD_VERIFIER_SYSTEM_PROMPT)
            result = parse_json_lenient(response_text)

            if not auto_enrich or result.get("verdict") == "PASS":
                break

            missing = result.get("missing_elements") or []
            if not missing:
                break

            enrich_prompt = build_brd_enrichment_prompt(working_text, project_meta, missing[:10])
            enrich_text = client.generate(enrich_prompt, BRD_ENRICHER_SYSTEM_PROMPT)
            enrichment = parse_json_lenient(enrich_text)
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
            "red_flags": [
                {"issue": "Failed to parse AI response into structured JSON.", "impact": "High"}
            ],
            "recommendations": ["Try verifying again. The AI model returned an invalid format."],
            "summary": f"JSON Parse Error: {str(e)}",
            "proceed_recommendation": "Proceed with Caution",
            "_debug": _error_debug(provider_name, e, response_preview=_truncate(getattr(e, "doc", ""), 6000)),
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


def extract_modules(brd_text, project_meta, provider_name, api_keys):
    client = determine_client(provider_name, api_keys)
    prompt = build_module_extraction_prompt(brd_text, project_meta)
    response_text = client.generate(prompt, MODULE_EXTRACT_SYSTEM_PROMPT)
    return parse_json_lenient(response_text)


def generate_gap_questions(brd_text, project_meta, provider_name, api_keys, verification_result):
    client = determine_client(provider_name, api_keys)
    prompt = build_brd_gap_questions_prompt(brd_text, project_meta, verification_result)
    response_text = client.generate(prompt, BRD_QUESTION_SYSTEM_PROMPT)
    return parse_json_lenient(response_text)


def generate_module_gap_questions(
    brd_text, project_meta, provider_name, api_keys, verification_result, module
):
    client = determine_client(provider_name, api_keys)
    prompt = build_module_gap_questions_prompt(
        brd_text, project_meta, module=module, verification_result=verification_result
    )
    response_text = client.generate(prompt, BRD_QUESTION_SYSTEM_PROMPT)
    return parse_json_lenient(response_text)


def enrich_brd_from_answers(brd_text, project_meta, provider_name, api_keys, questions_json, answers_json):
    client = determine_client(provider_name, api_keys)
    prompt = build_brd_enrichment_from_answers_prompt(
        brd_text, project_meta, questions_json, answers_json
    )
    response_text = client.generate(prompt, BRD_ENRICHER_SYSTEM_PROMPT)
    return parse_json_lenient(response_text)

