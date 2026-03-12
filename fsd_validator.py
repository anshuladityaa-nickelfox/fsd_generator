"""fsd_validator.py — FSD quality audit and auto-fix engine."""

import json
import logging
import traceback
from typing import Optional

from prompt_engine import (
    build_fsd_audit_prompt,
    build_fsd_section_fix_prompt,
    FSD_VALIDATOR_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
)
from llm_client import AutoClient, GroqClient, OpenAIClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Client factory (mirrors brd_core.determine_client)
# ---------------------------------------------------------------------------

def _make_client(provider: str, api_keys: dict):
    keys = api_keys or {}
    groq_model = keys.get("groq_model") or "llama-3.3-70b-versatile"
    openai_model = keys.get("openai_model") or "gpt-5.2"
    if provider == "Groq":
        return GroqClient(keys.get("groq"), model_name=groq_model)
    if provider == "OpenAI":
        return OpenAIClient(keys.get("openai"), model_name=openai_model)
    return AutoClient(
        keys.get("groq"),
        keys.get("openai"),
        groq_model=groq_model,
        openai_model=openai_model,
    )


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _strip_fences(text: str) -> str:
    s = (text or "").strip()
    if s.startswith("```"):
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1:]
        s = s.strip()
        if s.endswith("```"):
            s = s[:-3].strip()
    return s.strip()


def _parse_json(text: str):
    s = _strip_fences(text)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end > start:
            return json.loads(s[start:end + 1])
        raise


# ---------------------------------------------------------------------------
# Core: Audit the full FSD
# ---------------------------------------------------------------------------

def audit_fsd(
    fsd_sections: list,
    brd_text: str,
    project_meta: dict,
    provider: str,
    api_keys: dict,
) -> dict:
    """
    Audit the full FSD. Returns structured JSON with overall_status and per-section data.
    """
    full_fsd = "\n\n".join(
        [f"## {s.get('title', '')}\n\n{s.get('content', '')}" for s in fsd_sections]
    )
    client = _make_client(provider, api_keys)
    prompt = build_fsd_audit_prompt(full_fsd, brd_text, project_meta)
    try:
        raw = client.generate(prompt, FSD_VALIDATOR_SYSTEM_PROMPT)
        result = _parse_json(raw)
        return result
    except Exception as e:
        logger.exception("FSD audit failed")
        return {
            "overall_status": "ERROR",
            "overall_summary": f"Audit failed: {e}",
            "section_audits": [],
            "_error": str(e),
        }


# ---------------------------------------------------------------------------
# Core: Auto-fix the FSD
# ---------------------------------------------------------------------------

def auto_fix_fsd(
    fsd_sections: list,
    brd_text: str,
    project_meta: dict,
    settings: dict,
    provider: str,
    api_keys: dict,
    max_rounds: int = 3,
) -> dict:
    """
    Iteratively fix FSD sections with issues until overall_status is CLEAN or max_rounds.

    Returns:
        {
            "sections": [...],          # updated fsd_sections list
            "final_status": str,
            "initial_status": str,
            "rounds_taken": int,
            "fix_log": [{"round":1, "section":"...", "issues":[...]}],
            "audit_detail": {...},      # last audit result
        }
    """
    sections = [dict(s) for s in fsd_sections]  # shallow copy each section dict
    fix_log = []

    initial_result = audit_fsd(sections, brd_text, project_meta, provider, api_keys)
    initial_status = initial_result.get("overall_status", "NEEDS_FIX")
    
    client = _make_client(provider, api_keys)
    audit_detail = initial_result

    if initial_status == "CLEAN":
        return {
            "sections": sections,
            "final_status": initial_status,
            "initial_status": initial_status,
            "rounds_taken": 0,
            "fix_log": fix_log,
            "audit_detail": audit_detail,
        }

    for round_num in range(1, max_rounds + 1):
        section_audits = audit_detail.get("section_audits") or []

        # Build a lookup: section title → audit info
        audit_map = {}
        for sa in section_audits:
            key = (sa.get("section") or "").strip().lower()
            audit_map[key] = sa

        sections_fixed_this_round = 0

        for sec in sections:
            title = (sec.get("title") or "").strip()
            title_lower = title.lower()

            # Match by exact or partial title
            sa = audit_map.get(title_lower)
            if sa is None:
                # Try partial match
                for k, v in audit_map.items():
                    if title_lower in k or k in title_lower:
                        sa = v
                        break

            sec_status = (sa or {}).get("status", "CLEAN")
            if sec_status == "CLEAN":
                continue  # Skip clean sections

            issues = (sa or {}).get("issues") or []
            suggestions = (sa or {}).get("suggestions") or []

            fix_prompt = build_fsd_section_fix_prompt(
                section_name=title,
                current_content=sec.get("content", ""),
                brd_text=brd_text,
                project_meta=project_meta,
                issues=issues,
                suggestions=suggestions,
                settings=settings,
            )

            try:
                fixed_content = client.generate(fix_prompt, SYSTEM_PROMPT)
                log_entry = {
                    "round": round_num,
                    "section": title,
                    "issues": issues,
                }
                sec["content"] = fixed_content
                fix_log.append(log_entry)
                sections_fixed_this_round += 1
            except Exception as e:
                fix_log.append({
                    "round": round_num,
                    "section": title,
                    "error": str(e),
                })

        if sections_fixed_this_round == 0:
            break  # Nothing left to fix

        # Re-audit after this round
        audit_detail = audit_fsd(sections, brd_text, project_meta, provider, api_keys)
        new_status = audit_detail.get("overall_status", "NEEDS_FIX")

        if new_status == "CLEAN":
            break

    final_status = audit_detail.get("overall_status", "UNKNOWN")

    return {
        "sections": sections,
        "final_status": final_status,
        "initial_status": initial_status,
        "rounds_taken": round_num if sections_fixed_this_round > 0 else round_num - 1,
        "fix_log": fix_log,
        "audit_detail": audit_detail,
    }
