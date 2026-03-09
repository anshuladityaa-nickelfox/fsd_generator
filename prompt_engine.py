# prompt_engine.py

SYSTEM_PROMPT = """You are an expert Senior Business Analyst and Solutions Architect.
Your task is to convert Business Requirements Documents (BRDs) into detailed, technical, 
and highly structured Functional Specification Documents (FSDs).
You have a deep understanding of software engineering, system architecture, UX/UI, 
and product management. Provide professional, comprehensive, and actionable specifications.
Always output your response in Markdown."""

BRD_VERIFIER_SYSTEM_PROMPT = """You are a strict, senior Business Analyst reviewing a BRD to determine if it is ready to be converted into an FSD.
Analyze the provided document based on Completeness, Clarity, Consistency, Feasibility, and Testability.
You must return your analysis as a highly structured JSON object, exactly matching the format requested, without any markdown formatting around it.
"""

FSD_SECTIONS = [
    "1. Document Control & Approvals",
    "2. Project Overview & Objectives",
    "3. Scope of Work (In-Scope & Out-of-Scope)",
    "4. Target Audience & User Personas",
    "5. Use Cases & User Journeys",
    "6. Functional Requirements",
    "7. System Architecture & Components",
    "8. Data Models & Database Schema",
    "9. API Integrations & Webhooks",
    "10. UI/UX & Frontend Specifications",
    "11. Business Rules & Logic",
    "12. Security & Authentication",
    "13. Performance & Scalability",
    "14. Error Handling & Logging",
    "15. Non-Functional Requirements (NFRs)",
    "16. Reporting & Analytics",
    "17. Data Migration Strategy",
    "18. Testing & QA Strategy",
    "19. Deployment & DevOps Strategy",
    "20. Glossary & Appendices"
]

def build_section_prompt(section_name, brd_text, previous_summary, settings):
    depth = settings.get("depth", "Standard")
    examples = settings.get("examples", True)
    terminology = settings.get("terminology", "Standard FSD")
    language = settings.get("language", "English")

    style_guide = f"Write in {language}. Use {terminology} terminology. Depth of detail: {depth}."
    if examples:
        style_guide += " Provide concrete examples, sample JSON payloads, or mock data where relevant."

    return f"""
{style_guide}

Generate section EXACTLY titled: {section_name}

Here is the original BRD text:
---
{brd_text}
---

Here is a summary of previously generated FSD sections for context:
---
{previous_summary}
---

Focus ONLY on {section_name}. Ensure it logically follows from the BRD and the previous context.
Do not generate any other sections.
"""

def build_quality_eval_prompt(fsd_content):
    return f"""
Review the following generated FSD content for overall quality, completeness, and consistency.
Provide a brief qualitative assessment and a score out of 100.

FSD Content:
---
{fsd_content[:3000]} # Truncated for token limits, evaluate the tone and structure based on this sample.
...
---
"""

def build_brd_verification_prompt(brd_text, project_meta):
    return f"""
Please analyze the following BRD (Business Requirements Document).

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}

BRD Text:
---
{brd_text}
---

You MUST output ONLY a valid JSON object with the following structure:
{{
  "verdict": "PASS | WARN | FAIL",
  "overall_score": 85,
  "brd_type_detected": "e.g., E-commerce Platform, Internal Tool",
  "is_valid_brd": true,
  "confidence": "High | Medium | Low",
  "dimensions": {{
    "completeness": {{"score": 80, "status": "Good", "detail": "Missing some edge cases."}},
    "clarity": {{"score": 90, "status": "Excellent", "detail": "Very clear and unambiguous."}},
    "consistency": {{"score": 85, "status": "Good", "detail": "Consistent terminology used."}},
    "feasibility": {{"score": 75, "status": "Fair", "detail": "Some complex integrations."}},
    "testability": {{"score": 80, "status": "Good", "detail": "Acceptance criteria present for most features."}}
  }},
  "present_elements": ["List of elements found in the BRD"],
  "missing_elements": ["List of elements completely missing from the BRD"],
  "red_flags": [
    {{"issue": "Brief description of critical issue", "impact": "High"}}
  ],
  "recommendations": ["Actionable steps to improve the BRD before FSD generation"],
  "summary": "A 2-3 sentence summary of the BRD quality.",
  "proceed_recommendation": "Strongly Advise Proceeding | Proceed with Caution | Do Not Proceed"
}}

Ensure valid JSON syntax (no trailing commas, double quotes for keys). Do not wrap in ```json ``` blocks. If the document is fundamentally not a BRD or is completely empty/gibberish, set `is_valid_brd` to false, verdict to FAIL, and provide appropriate feedback.
"""
