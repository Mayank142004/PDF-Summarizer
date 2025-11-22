# Universal Credit Act 2025 Analyzer

A standalone Streamlit application that analyzes legislative documents using AI. This tool extracts text from PDFs, summarizes acts, extracts key legislative sections, and performs compliance rule checks.

## Features

- **Task 1: Extract Text** - Extract clean, structured text from PDF documents
- **Task 2: Summarize** - Generate 5-10 bullet point summaries focusing on purpose, definitions, eligibility, obligations, and enforcement
- **Task 3: Extract Sections** - Extract key legislative sections (definitions, obligations, responsibilities, eligibility, payments, penalties, record-keeping)
- **Task 4: Rule Checks** - Apply 6 compliance rules with evidence and confidence scores

## Requirements

- Python 3.8+
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd assn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. In the sidebar:
   - Enter your OpenAI API key
   - Choose input method:
     - **Upload PDF File**: Upload the Universal Credit Act 2025 PDF
     - **Paste Text**: Paste the full text of the Act in the text area

3. Click "Run All Tasks" or run tasks individually:
   - Task 1: Extract Text (automatic when file is uploaded)
   - Task 2: Summarize
   - Task 3: Extract Sections
   - Task 4: Check Rules

4. View results and download the final JSON report

## Output Format

The application generates a structured JSON report with:

```json
{
  "summary": "5-10 bullet point summary of the Act",
  "sections": {
    "definitions": "...",
    "obligations": "...",
    "responsibilities": "...",
    "eligibility": "...",
    "payments": "...",
    "penalties": "...",
    "record_keeping": "..."
  },
  "rule_checks": [
    {
      "rule": "Act must define key terms",
      "status": "pass",
      "evidence": "Section 2 – Definitions",
      "confidence": 92
    },
    ...
  ]
}
```

## Rule Checks

The application checks for 6 compliance rules:

1. Act must define key terms
2. Act must specify eligibility criteria
3. Act must specify responsibilities of the administering authority
4. Act must include enforcement or penalties
5. Act must include payment calculation or entitlement structure
6. Act must include record-keeping or reporting requirements

## Notes

- The application uses OpenAI's GPT-4o-mini model for analysis
- Large documents may be truncated to fit token limits
- Ensure you have sufficient API credits for document analysis

## License

This project is created for the NIYAMR AI 48-Hour Internship Assignment.

