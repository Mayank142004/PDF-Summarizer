import streamlit as st
import json
import os
from typing import Dict, List, Optional
import openai
from PyPDF2 import PdfReader
import io

# Page configuration
st.set_page_config(
    page_title="Universal Credit Act 2025 Analyzer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'sections' not in st.session_state:
    st.session_state.sections = None
if 'rule_checks' not in st.session_state:
    st.session_state.rule_checks = None

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file."""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def summarize_act(text: str, api_key: str) -> str:
    """Summarize the Act in 5-10 bullet points."""
    client = openai.OpenAI(api_key=api_key)
    
    prompt = """Summarize the following Act in 5-10 bullet points focusing on:
- Purpose
- Key definitions
- Eligibility
- Obligations
- Enforcement elements

Act text:
{}

Provide a clear, structured summary with bullet points.""".format(text[:15000])  # Limit text to avoid token limits
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal document analyst. Provide clear, concise summaries of legislative documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return ""

def extract_legislative_sections(text: str, api_key: str) -> Dict:
    """Extract key legislative sections."""
    client = openai.OpenAI(api_key=api_key)
    
    # Define JSON schema for strict mode
    schema = {
        "type": "object",
        "properties": {
            "definitions": {
                "type": "string",
                "description": "Extract all key definitions and terms"
            },
            "obligations": {
                "type": "string",
                "description": "Extract all obligations mentioned in the Act"
            },
            "responsibilities": {
                "type": "string",
                "description": "Extract responsibilities of the administering authority"
            },
            "eligibility": {
                "type": "string",
                "description": "Extract eligibility criteria"
            },
            "payments": {
                "type": "string",
                "description": "Extract payment calculations, entitlements, and payment structures"
            },
            "penalties": {
                "type": "string",
                "description": "Extract penalties and enforcement mechanisms"
            },
            "record_keeping": {
                "type": "string",
                "description": "Extract record-keeping and reporting requirements"
            }
        },
        "required": ["definitions", "obligations", "responsibilities", "eligibility", "payments", "penalties", "record_keeping"],
        "additionalProperties": False
    }
    
    prompt = f"""Extract the following key sections from the Act and return a valid JSON object:

- definitions: Extract all key definitions and terms
- obligations: Extract all obligations mentioned in the Act
- responsibilities: Extract responsibilities of the administering authority
- eligibility: Extract eligibility criteria
- payments: Extract payment calculations, entitlements, and payment structures
- penalties: Extract penalties and enforcement mechanisms
- record_keeping: Extract record-keeping and reporting requirements

Act text:
{text[:15000]}

Return ONLY the JSON object matching the required schema, no additional text."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal document analyst. Extract structured information and return ONLY valid JSON matching the exact schema."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "legislative_sections",
                    "strict": True,
                    "schema": schema
                }
            }
        )
        content = response.choices[0].message.content
        # Parse JSON
        return json.loads(content)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"Error extracting sections: {str(e)}")
        return {}

def check_rules(text: str, api_key: str) -> List[Dict]:
    """Apply 6 rule checks to the Act."""
    client = openai.OpenAI(api_key=api_key)
    
    rules = [
        "Act must define key terms",
        "Act must specify eligibility criteria",
        "Act must specify responsibilities of the administering authority",
        "Act must include enforcement or penalties",
        "Act must include payment calculation or entitlement structure",
        "Act must include record-keeping or reporting requirements"
    ]
    
    # Define JSON schema for strict mode
    schema = {
        "type": "object",
        "properties": {
            "rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rule": {
                            "type": "string",
                            "description": "The rule being checked"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pass", "fail"],
                            "description": "Whether the rule passes or fails"
                        },
                        "evidence": {
                            "type": "string",
                            "description": "The specific section, clause, or text that supports the answer"
                        },
                        "confidence": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Confidence level between 0-100"
                        }
                    },
                    "required": ["rule", "status", "evidence", "confidence"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["rules"],
        "additionalProperties": False
    }
    
    rules_text = "\n".join([f"{i+1}. {rule}" for i, rule in enumerate(rules)])
    prompt = f"""For each of the following rules, check if the Act satisfies it. For each rule, provide:
1. status: "pass" or "fail"
2. evidence: The specific section, clause, or text that supports your answer
3. confidence: A number between 0-100 indicating your confidence level

Rules to check:
{rules_text}

Act text:
{text[:15000]}

Return a JSON object with a "rules" key containing an array with the exact structure specified in the schema."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal compliance checker. Analyze documents and return structured rule checks in JSON format matching the exact schema."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "rule_checks",
                    "strict": True,
                    "schema": schema
                }
            }
        )
        content = response.choices[0].message.content
        
        # Parse JSON
        result = json.loads(content)
        if isinstance(result, dict) and "rules" in result:
            return result["rules"]
        else:
            st.error("Unexpected response structure")
            return [{"rule": rule, "status": "unknown", "evidence": "Could not parse", "confidence": 0} for rule in rules]
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {str(e)}")
        return [{"rule": rule, "status": "error", "evidence": f"JSON parse error: {str(e)}", "confidence": 0} for rule in rules]
    except Exception as e:
        st.error(f"Error checking rules: {str(e)}")
        return [{"rule": rule, "status": "error", "evidence": str(e), "confidence": 0} for rule in rules]

def generate_final_report(summary: str, sections: Dict, rule_checks: List[Dict]) -> Dict:
    """Generate the final structured JSON report."""
    return {
        "summary": summary,
        "sections": sections,
        "rule_checks": rule_checks
    }

# Main UI
st.title("📄 Universal Credit Act 2025 Analyzer")
st.markdown("AI Agent for Reading, Summarizing, and Analyzing Legislative Documents")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key"
    )
    
    st.divider()
    
    # File upload
    st.subheader("📁 Document Input")
    upload_option = st.radio(
        "Choose input method:",
        ["Upload PDF File", "Paste Text"]
    )
    
    text_input = None
    
    if upload_option == "Upload PDF File":
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            help="Upload the Universal Credit Act 2025 PDF"
        )
        if uploaded_file:
            if st.button("Extract Text from PDF", use_container_width=True):
                with st.spinner("Extracting text from PDF..."):
                    st.session_state.extracted_text = extract_text_from_pdf(uploaded_file)
                    if st.session_state.extracted_text:
                        st.success(f"✅ Extracted {len(st.session_state.extracted_text)} characters")
    else:
        text_input = st.text_area(
            "Paste Act Text",
            height=200,
            help="Paste the full text of the Act here"
        )
        if st.button("Use Pasted Text", use_container_width=True):
            if text_input:
                st.session_state.extracted_text = text_input
                st.success(f"✅ Loaded {len(st.session_state.extracted_text)} characters")

# Main content area
if not api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to begin.")
    st.stop()

if not st.session_state.extracted_text:
    st.info("👆 Please upload a PDF file or paste text in the sidebar to begin.")
    st.stop()

# Display extracted text preview
with st.expander("📋 Extracted Text Preview", expanded=False):
    st.text_area("Text", st.session_state.extracted_text, height=200, disabled=True)
    st.caption(f"Total characters: {len(st.session_state.extracted_text)}")

# Task buttons
st.header("🔍 Analysis Tasks")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📝 Task 1: Extract Text", use_container_width=True):
        st.success("✅ Text already extracted!")

with col2:
    if st.button("📊 Task 2: Summarize", use_container_width=True):
        if st.session_state.extracted_text:
            with st.spinner("Generating summary..."):
                st.session_state.summary = summarize_act(st.session_state.extracted_text, api_key)

with col3:
    if st.button("🔎 Task 3: Extract Sections", use_container_width=True):
        if st.session_state.extracted_text:
            with st.spinner("Extracting legislative sections..."):
                st.session_state.sections = extract_legislative_sections(st.session_state.extracted_text, api_key)

with col4:
    if st.button("✅ Task 4: Check Rules", use_container_width=True):
        if st.session_state.extracted_text:
            with st.spinner("Checking compliance rules..."):
                st.session_state.rule_checks = check_rules(st.session_state.extracted_text, api_key)

# Run all tasks button
if st.button("🚀 Run All Tasks", type="primary", use_container_width=True):
    if st.session_state.extracted_text:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Task 2
        status_text.text("Task 2: Summarizing Act...")
        progress_bar.progress(25)
        st.session_state.summary = summarize_act(st.session_state.extracted_text, api_key)
        
        # Task 3
        status_text.text("Task 3: Extracting legislative sections...")
        progress_bar.progress(50)
        st.session_state.sections = extract_legislative_sections(st.session_state.extracted_text, api_key)
        
        # Task 4
        status_text.text("Task 4: Checking compliance rules...")
        progress_bar.progress(75)
        st.session_state.rule_checks = check_rules(st.session_state.extracted_text, api_key)
        
        progress_bar.progress(100)
        status_text.text("✅ All tasks completed!")
        st.success("All analysis tasks completed successfully!")

# Display results
if st.session_state.summary:
    st.header("📊 Task 2: Summary")
    st.markdown(st.session_state.summary)

if st.session_state.sections:
    st.header("🔎 Task 3: Key Legislative Sections")
    
    tabs = st.tabs(["Definitions", "Obligations", "Responsibilities", "Eligibility", "Payments", "Penalties", "Record Keeping"])
    
    with tabs[0]:
        st.write(st.session_state.sections.get("definitions", "Not found"))
    with tabs[1]:
        st.write(st.session_state.sections.get("obligations", "Not found"))
    with tabs[2]:
        st.write(st.session_state.sections.get("responsibilities", "Not found"))
    with tabs[3]:
        st.write(st.session_state.sections.get("eligibility", "Not found"))
    with tabs[4]:
        st.write(st.session_state.sections.get("payments", "Not found"))
    with tabs[5]:
        st.write(st.session_state.sections.get("penalties", "Not found"))
    with tabs[6]:
        st.write(st.session_state.sections.get("record_keeping", "Not found"))

if st.session_state.rule_checks:
    st.header("✅ Task 4: Rule Checks")
    
    for i, check in enumerate(st.session_state.rule_checks):
        status_emoji = "✅" if check.get("status", "").lower() == "pass" else "❌"
        confidence = check.get("confidence", 0)
        
        with st.expander(f"{status_emoji} Rule {i+1}: {check.get('rule', 'Unknown')} (Confidence: {confidence}%)"):
            st.write(f"**Status:** {check.get('status', 'Unknown')}")
            st.write(f"**Evidence:** {check.get('evidence', 'No evidence provided')}")
            st.write(f"**Confidence:** {confidence}%")

# Generate and download final report
if st.session_state.summary and st.session_state.sections and st.session_state.rule_checks:
    st.header("📥 Final Report")
    
    final_report = generate_final_report(
        st.session_state.summary,
        st.session_state.sections,
        st.session_state.rule_checks
    )
    
    # Display JSON
    st.json(final_report)
    
    # Download button
    json_str = json.dumps(final_report, indent=2)
    st.download_button(
        label="📥 Download JSON Report",
        data=json_str,
        file_name="universal_credit_act_2025_analysis.json",
        mime="application/json",
        use_container_width=True
    )

