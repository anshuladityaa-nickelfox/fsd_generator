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
Be concrete: use short, specific findings (not generic advice). Prefer evidence-based notes tied to the BRD text.
You MUST output ONLY a valid JSON object.
Do NOT ask for information that is already provided in the BRD or in the Tech Stack field.
"""

BRD_ENRICHER_SYSTEM_PROMPT = """You are a senior Business Analyst improving a draft BRD so it can be converted into an implementation-ready FSD.
You may propose reasonable assumptions, but you MUST clearly label assumptions as assumptions and avoid inventing real names, emails, or company-specific facts not present in the BRD.
You MUST output ONLY a valid JSON object.
"""

BRD_QUESTION_SYSTEM_PROMPT = """You are a senior Business Analyst running a structured requirements clarification interview.
Your goal is to ask a SMALL number of high-impact questions that will unblock writing an implementation-ready FSD.
You MUST output ONLY a valid JSON object.
"""

MODULE_EXTRACT_SYSTEM_PROMPT = """You are a senior Business Analyst. Extract functional modules/features from a BRD.
Return only JSON.
"""

FSD_VALIDATOR_SYSTEM_PROMPT = """You are a rigorous FSD Quality Auditor. Your job is to evaluate a Functional Specification Document against the original BRD and FSD best-practice standards.
Identify vagueness, missing acceptance criteria, absent error states, TBDs without justification, and misalignment with the BRD.
Focus on identifying specific actionable issues that need fixing to make the document developer-ready.
You MUST output ONLY a valid JSON object.
"""

BRD_EXPECTED_ELEMENTS = [
    "Project background / problem statement",
    "Tech stack / architecture (user-provided is acceptable)",
    "Goals / objectives and success metrics",
    "Target users / personas",
    "Scope (in-scope) and out-of-scope",
    "Assumptions and constraints",
    "Functional requirements (feature-level)",
    "Use cases / user scenarios",
    "User journeys / user flows",
    "Data requirements (inputs/outputs) and sample data",
    "Business rules and validation rules",
    "Integrations / external dependencies",
    "Non-functional requirements (performance, security, usability, accessibility, etc.)",
    "Error/edge cases and exception flows",
    "Acceptance criteria and test considerations",
    "Risks and mitigations",
    "Stakeholders / owners and roles (optional for initial draft; can be TBD)",
]

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

SECTION_CHECKLISTS = {
    "1. Document Control & Approvals": [
        "Version history table (date, author, change summary)",
        "Approvals/sign-off table (name, role, approval status, date)",
        "Document audience and how to use this document",
        "Assumptions/constraints that affect approval scope",
    ],
    "2. Project Overview & Objectives": [
        "Problem statement and business context",
        "Objectives, success metrics (KPIs), and non-goals",
        "Stakeholders/owners and high-level responsibilities",
        "High-level solution overview (what the system will do)",
    ],
    "3. Scope of Work (In-Scope & Out-of-Scope)": [
        "In-scope features and out-of-scope items",
        "Constraints (timeline, budget, regulatory, technical)",
        "Dependencies (teams, vendors, systems)",
        "Risks + mitigations (top 5)",
    ],
    "4. Target Audience & User Personas": [
        "User roles/personas with goals and pain points",
        "Permission/role matrix if applicable",
        "Accessibility and localization considerations (if relevant)",
    ],
    "5. Use Cases & User Journeys": [
        "Use cases with ID, actor, preconditions, trigger, main flow",
        "Alternate flows + exception flows",
        "Post-conditions (system state after completion)",
        "User flow diagram (use Mermaid when helpful)",
    ],
    "6. Functional Requirements": [
        "Requirements list with IDs (FR-001…), priority (Must/Should/Could)",
        "Acceptance criteria per requirement (Given/When/Then where possible)",
        "Inputs/outputs, validations, and error states",
        "Traceability: map requirements back to BRD statements where possible",
        "Open questions/TBDs when BRD is unclear (avoid guessing)",
    ],
    "7. System Architecture & Components": [
        "Component diagram (Mermaid) and responsibilities",
        "Runtime flows for key operations",
        "Tech assumptions and constraints (if BRD does not specify, mark TBD)",
    ],
    "8. Data Models & Database Schema": [
        "Entities, relationships, key fields, constraints",
        "Data ownership/source of truth per domain object",
        "Retention, privacy, and audit considerations (if relevant)",
    ],
    "9. API Integrations & Webhooks": [
        "External systems, auth method, rate limits, failure modes",
        "Endpoint specs (method, path, request/response examples when allowed)",
        "Idempotency, retries, timeouts, and webhook verification",
    ],
    "10. UI/UX & Frontend Specifications": [
        "Screens/pages list and navigation",
        "Form fields (name, type, validation rules, error copy)",
        "Empty/loading/error states",
        "Responsive behavior and accessibility notes",
    ],
    "11. Business Rules & Logic": [
        "Rules catalog (BR-001…) with conditions and outcomes",
        "Validation and calculation rules",
        "State machines/workflow rules (Mermaid if helpful)",
    ],
    "12. Security & Authentication": [
        "AuthN/AuthZ approach, roles/permissions",
        "Sensitive data handling (PII), encryption, secrets",
        "Audit logging requirements",
    ],
    "13. Performance & Scalability": [
        "SLOs/SLAs (latency, throughput) if known, else TBD",
        "Capacity assumptions and scaling strategy",
        "Caching and rate limiting notes",
    ],
    "14. Error Handling & Logging": [
        "Error taxonomy (user errors vs system errors)",
        "Logging events, severity, correlation IDs",
        "Monitoring/alerting signals and runbook pointers (TBD if unknown)",
    ],
    "15. Non-Functional Requirements (NFRs)": [
        "Security, performance, reliability, maintainability",
        "Accessibility (WCAG), usability, localization (if relevant)",
        "Compliance/regulatory constraints (if applicable)",
    ],
    "16. Reporting & Analytics": [
        "KPIs/metrics, dashboards, event taxonomy",
        "Audit/compliance reporting needs",
    ],
    "17. Data Migration Strategy": [
        "Sources, mapping, validation approach",
        "Cutover plan and rollback considerations",
    ],
    "18. Testing & QA Strategy": [
        "Test types (unit/integration/e2e), environments",
        "Acceptance test scenarios mapped to FRs",
        "Test data strategy and edge cases",
    ],
    "19. Deployment & DevOps Strategy": [
        "Environments, CI/CD, config management",
        "Rollout strategy (feature flags, phased rollout)",
        "Observability and incident response basics",
    ],
    "20. Glossary & Appendices": [
        "Glossary of domain terms and acronyms",
        "Open questions / TBD list",
        "References/links (if provided in BRD)",
    ],
}

def build_section_prompt(section_name, brd_text, previous_summary, settings):
    depth = settings.get("depth", "Standard")
    examples = settings.get("examples", True)
    terminology = settings.get("terminology", "Standard FSD")
    language = settings.get("language", "English")

    style_guide = f"Write in {language}. Use {terminology} terminology. Depth of detail: {depth}."
    if examples:
        style_guide += " Provide concrete examples, sample JSON payloads, or mock data where relevant."

    checklist = SECTION_CHECKLISTS.get(section_name, [])
    checklist_text = ""
    if checklist:
        checklist_text = "\nRequired coverage checklist:\n- " + "\n- ".join(checklist) + "\n"

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
If the BRD is missing required information, do NOT invent details; explicitly mark them as **TBD** and list the exact questions needed to unblock implementation.
{checklist_text}
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
    expected = "\n- " + "\n- ".join(BRD_EXPECTED_ELEMENTS)
    return f"""
Please analyze the following BRD (Business Requirements Document).

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}
Tech Stack (if provided by user): {project_meta.get('tech_stack', 'Not provided')}

BRD Text:
---
{brd_text}
---

Evaluate the BRD against this checklist of expected BRD elements (use this list to populate present/missing elements where applicable):
{expected}

When producing `missing_elements`, order them by impact on successfully producing an implementation-ready FSD (prioritize flows, requirements, data, rules, and acceptance criteria). Do NOT prioritize missing stakeholder/owner names.
If Tech Stack is provided, treat "Tech stack / architecture" as PRESENT and do not list it as missing. Instead, if the BRD mentions integrations, then the missing item should be specific integration details (e.g., provider name, API endpoints, auth method, webhooks, error codes), not generic "technical requirements".
Avoid generic placeholders like "detailed technical specifications"; make missing items actionable and specific.

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
    {{"issue": "Brief description of critical issue", "impact": "Critical | High | Medium | Low"}}
  ],
  "recommendations": ["Actionable steps to improve the BRD before FSD generation"],
  "summary": "A 2-3 sentence summary of the BRD quality.",
  "proceed_recommendation": "Strongly Advise Proceeding | Proceed with Caution | Do Not Proceed"
}}

Ensure valid JSON syntax (no trailing commas, double quotes for keys). Do not wrap in ```json ``` blocks. If the document is fundamentally not a BRD or is completely empty/gibberish, set `is_valid_brd` to false, verdict to FAIL, and provide appropriate feedback.
Scoring guidance:
- PASS: overall_score >= 85 AND no Critical red flags AND most checklist items are present.
- WARN: overall_score 60–84 OR notable missing items that can be clarified quickly.
- FAIL: overall_score < 60 OR any Critical red flags OR the document is not a BRD.
"""

def build_brd_enrichment_prompt(brd_text, project_meta, missing_elements):
    missing = ", ".join(missing_elements or [])
    return f"""
You are improving a BRD draft by adding a concise addendum that fills gaps.

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}
Tech Stack (user-provided): {project_meta.get('tech_stack', 'Not provided')}

Missing elements to address (highest impact first):
{missing}

Original BRD:
---
{brd_text}
---

You MUST output ONLY a valid JSON object with this structure:
{{
  "addendum_markdown": "A BRD addendum in Markdown that adds the missing elements. Use headings. Keep it concise but actionable.",
  "assumptions": ["List of explicit assumptions you made (each must be verifiable by the user)."],
  "open_questions": ["Questions for the user to confirm/clarify remaining unknowns."],
  "filled_elements": ["Which missing elements you addressed (from the list provided)."]
}}

Rules:
- Do NOT invent stakeholder/owner names. If needed, write 'TBD' and describe the role (e.g., 'Product Owner (TBD)'). 
- Prefer structured content: bullets, tables, and (if relevant) Mermaid diagrams for user flows.
- If tech stack is provided, reflect it in integrations, data, hosting, auth, and logging assumptions where applicable (still label as assumptions).
"""

def build_brd_gap_questions_prompt(brd_text, project_meta, verification_result):
    missing = verification_result.get("missing_elements") if isinstance(verification_result, dict) else []
    red_flags = verification_result.get("red_flags") if isinstance(verification_result, dict) else []
    missing_text = "\n- " + "\n- ".join((missing or [])[:12]) if missing else "None"
    red_flags_text = ""
    if red_flags:
        red_flags_text = "\n- " + "\n- ".join(
            [f"{rf.get('impact','')}: {rf.get('issue','')}" for rf in red_flags[:8]]
        )
    return f"""
You are given a BRD and its verification report. Generate clarification questions for the user.

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}
Tech Stack (user-provided): {project_meta.get('tech_stack', 'Not provided')}

Highest-impact missing elements (ordered):
{missing_text}

Red flags:
{red_flags_text or "None"}

BRD:
---
{brd_text}
---

Constraints:
- Ask max 7 questions total.
- Prefer multiple-choice (single_select/multi_select) over free text.
- Do NOT ask for stakeholder/owner NAMES as a priority; use roles if needed.
- Ask module-by-module when possible.
- Each question should be answerable without deep technical knowledge, but should collect details needed for FSD (flows, data, rules, acceptance criteria, actions/side effects).

You MUST output ONLY a valid JSON object with this structure:
{{
  "questions": [
    {{
      "id": "Q1",
      "topic": "e.g., User Flows",
      "type": "single_select | multi_select | text | number | boolean",
      "question": "Question text",
      "options": ["Option 1", "Option 2"],
      "required": true,
      "help": "1 short sentence why this matters",
      "default": null
    }}
  ]
}}
"""


def build_brd_enrichment_from_answers_prompt(brd_text, project_meta, questions, answers):
    return f"""
You are improving a BRD draft by adding a concise addendum that incorporates user answers from a clarification round.

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}
Tech Stack (user-provided): {project_meta.get('tech_stack', 'Not provided')}

Clarification questions asked (JSON):
{questions}

User answers (JSON):
{answers}

Original BRD:
---
{brd_text}
---

You MUST output ONLY a valid JSON object with this structure:
{{
  "addendum_markdown": "A BRD addendum in Markdown that adds missing details based on the answers. Use headings. Keep it concise but actionable.",
  "assumptions": ["Any remaining assumptions you had to make (must be explicit)."],
  "open_questions": ["Any remaining questions that still block an implementation-ready FSD."],
  "filled_elements": ["Which BRD/FSD elements are now better defined after applying the answers."]
}}

Rules:
- Do NOT invent stakeholder/owner names. Use roles + 'TBD' if needed.
- Convert vague answers into concrete, testable statements (include validations, edge cases, acceptance criteria).
- Include Actions + Side Effects (UI and backend) for key user operations mentioned in answers.
"""


def build_module_extraction_prompt(brd_text, project_meta):
    return f"""
Extract functional modules/features from this BRD. A module is a cohesive set of functionality around a business entity or process.

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}
Tech Stack (user-provided): {project_meta.get('tech_stack', 'Not provided')}

BRD:
---
{brd_text}
---

You MUST output ONLY a valid JSON object with this structure:
{{
  "modules": [
    {{
      "id": "kebab-case-id",
      "name": "Module Name",
      "description": "1-2 sentence description",
      "primary_entities": ["EntityA", "EntityB"],
      "key_user_actions": ["Action 1", "Action 2"]
    }}
  ]
}}

Rules:
- Keep it to 3–12 modules (merge duplicates; don’t explode into tiny items).
- Prefer business-level module names (e.g., User Management, Orders, Payments, Reporting).
- If BRD is vague, propose a sensible module breakdown but keep descriptions conservative.
"""


def build_module_gap_questions_prompt(brd_text, project_meta, module, verification_result):
    missing = verification_result.get("missing_elements") if isinstance(verification_result, dict) else []
    red_flags = verification_result.get("red_flags") if isinstance(verification_result, dict) else []
    missing_text = "\n- " + "\n- ".join((missing or [])[:12]) if missing else "None"
    red_flags_text = ""
    if red_flags:
        red_flags_text = "\n- " + "\n- ".join(
            [f"{rf.get('impact','')}: {rf.get('issue','')}" for rf in red_flags[:8]]
        )
    module_json = module or {}
    return f"""
You are generating clarification questions for ONE module, based on a BRD and its verification report.

Project Name: {project_meta.get('name', 'Unknown')}
Context: {project_meta.get('context', 'None provided')}
Tech Stack (user-provided): {project_meta.get('tech_stack', 'Not provided')}

Current module (JSON):
{module_json}

Highest-impact missing elements (ordered):
{missing_text}

Red flags:
{red_flags_text or "None"}

BRD:
---
{brd_text}
---

Constraints:
- Ask max 7 questions total.
- Prefer multiple-choice (single_select/multi_select) over free text.
- Do NOT ask for stakeholder/owner NAMES as a priority; use roles if needed.
- Focus on this module’s: user flows, data fields, business rules, workflow/states, actions + side effects, acceptance criteria.

You MUST output ONLY a valid JSON object with this structure:
{{
  "module_id": "{module_json.get('id','')}",
  "questions": [
    {{
      "id": "Q1",
      "topic": "e.g., User Flows",
      "type": "single_select | multi_select | text | number | boolean",
      "question": "Question text",
      "options": ["Option 1", "Option 2"],
      "required": true,
      "help": "1 short sentence why this matters",
      "default": null
    }}
  ]
}}
"""


def build_fsd_audit_prompt(full_fsd: str, brd_text: str, project_meta: dict) -> str:
    """Returns a JSON-structured quality audit of the full FSD."""
    fsd_sample = full_fsd[:12000]
    brd_sample = brd_text[:4000]
    name = project_meta.get("name", "Unknown")
    context = project_meta.get("context", "None provided")
    tech = project_meta.get("tech_stack", "Not provided")
    return (
        "You are auditing the following Functional Specification Document (FSD) against its source BRD.\n\n"
        f"Project: {name}\nContext: {context}\nTech Stack: {tech}\n\n"
        "Source BRD (truncated):\n---\n"
        f"{brd_sample}\n---\n\n"
        "FSD content (truncated for token limits):\n---\n"
        f"{fsd_sample}\n...\n---\n\n"
        "For each FSD section present, identify specific issues or gaps.\n\n"
        "You MUST output ONLY a valid JSON object with this structure:\n"
        "{\n"
        '  "overall_status": "CLEAN | NEEDS_FIX | CRITICAL_GAPS",\n'
        '  "overall_summary": "Brief 2-3 sentence summary of FSD quality and main weaknesses.",\n'
        '  "section_audits": [\n'
        "    {\n"
        '      "section": "Section title (e.g. 6. Functional Requirements)",\n'
        '      "status": "CLEAN | NEEDS_FIX",\n'
        '      "issues": ["Missing acceptance criteria for FR-003"],\n'
        '      "suggestions": ["Add Given/When/Then acceptance criteria for each FR"]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Status guidance:\n"
        "- CLEAN: Section or document is complete, specific, actionable, and aligns with BRD.\n"
        "- NEEDS_FIX: There are minor to moderate omissions, vagueness, or TBDs that can be resolved.\n"
        "- CRITICAL_GAPS: Major sections are missing or the document fundamentally fails to address the BRD requirements.\n\n"
        "Do not wrap output in ```json``` blocks. Ensure valid JSON syntax.\n"
    )


def build_fsd_section_fix_prompt(
    section_name: str,
    current_content: str,
    brd_text: str,
    project_meta: dict,
    issues: list,
    suggestions: list,
    settings: dict,
) -> str:
    """Prompt to rewrite a single FSD section to fix identified issues."""
    depth = settings.get("depth", "Standard")
    language = settings.get("language", "English")
    terminology = settings.get("terminology", "Standard FSD")
    examples = settings.get("examples", True)

    style_guide = f"Write in {language}. Use {terminology} terminology. Depth: {depth}."
    if examples:
        style_guide += " Include concrete examples, sample data, or Mermaid diagrams where relevant."

    issues_text = "\n".join([f"- {i}" for i in (issues or [])]) or "None reported."
    suggestions_text = "\n".join([f"- {s}" for s in (suggestions or [])]) or "None."
    brd_sample = brd_text[:3000]
    name = project_meta.get("name", "Unknown")

    return (
        f"{style_guide}\n\n"
        "You are rewriting a single FSD section to fix quality issues identified by an AI auditor.\n\n"
        f"Project: {name}\n"
        "BRD excerpt (for alignment context):\n---\n"
        f"{brd_sample}\n...\n---\n\n"
        f"Section to fix: {section_name}\n\n"
        "Current content:\n---\n"
        f"{current_content}\n---\n\n"
        f"Identified issues (must be fixed):\n{issues_text}\n\n"
        f"Suggested improvements:\n{suggestions_text}\n\n"
        "Instructions:\n"
        f'- Output ONLY the rewritten markdown content for section "{section_name}".\n'
        f'- Do NOT change the section title - keep it as "{section_name}".\n'
        "- Do NOT output any other sections.\n"
        "- Address every listed issue.\n"
        "- Do NOT add fictional names, emails, or company-specific facts not in the BRD.\n"
        "- Mark remaining unknowns as **TBD** with a brief explanation.\n"
        "- Be specific, structured, and developer-ready.\n"
    )
