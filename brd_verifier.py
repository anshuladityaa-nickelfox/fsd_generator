import json
import streamlit as st
from prompt_engine import build_brd_verification_prompt, BRD_VERIFIER_SYSTEM_PROMPT
from llm_client import AutoClient, GroqClient, GeminiClient

def determine_client(provider, keys):
    if provider == "Groq":
        return GroqClient(keys.get("groq"))
    elif provider == "Gemini":
        return GeminiClient(keys.get("gemini"))
    else:
        return AutoClient(keys.get("groq"), keys.get("gemini"))

def verify_brd(brd_text, project_meta, provider_name, api_keys):
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

    try:
        client = determine_client(provider_name, api_keys)
        prompt = build_brd_verification_prompt(brd_text, project_meta)
        
        response_text = client.generate(prompt, BRD_VERIFIER_SYSTEM_PROMPT)
        
        # Strip markdown json block if model returned it despite instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        result = json.loads(response_text.strip())
        return result
        
    except json.JSONDecodeError as e:
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
            "proceed_recommendation": "Proceed with Caution"
        }
    except Exception as e:
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
            "proceed_recommendation": "Do Not Proceed"
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
        st.markdown(f"""
        <div class="red-flag-card">
            <strong>{flag.get('impact', 'High')} Impact:</strong> {flag.get('issue', '')}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Recommendations")
    for rec in result.get("recommendations", []):
        st.markdown(f"""
        <div class="rec-card">
            {rec}
        </div>
        """, unsafe_allow_html=True)
