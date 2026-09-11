import json
from app.services.llm_service import ask_llm

EXTRACTION_PROMPT_TEMPLATE = """You are a research paper analysis assistant. Read the paper text below and extract exactly these 8 fields.

Return ONLY a valid JSON object with these exact keys, nothing else — no markdown formatting, no explanation, no code fences:
- research_problem
- method_used
- dataset
- algorithm
- results
- advantage
- limitation
- future_scope

Rules:
- Each value should be a concise 1-3 sentence summary in your own words.
- If a field genuinely cannot be found in the text, use the string "Not specified" as its value.
- Do not include any text before or after the JSON object.

Paper text:
---
{paper_text}
---

JSON output:"""


def build_extraction_prompt(paper_text: str) -> str:
    return EXTRACTION_PROMPT_TEMPLATE.format(paper_text=paper_text)
def extract_fields_from_text(paper_text: str, max_attempts: int = 2) -> dict:
    """Call the LLM to extract the 8 fields, retrying once if JSON parsing fails."""
    prompt = build_extraction_prompt(paper_text)

    for attempt in range(max_attempts):
        raw_response = ask_llm(prompt, max_tokens=800)
        cleaned = raw_response.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        try:
            data = json.loads(cleaned)
            return data  # success — return immediately
        except json.JSONDecodeError:
            if attempt < max_attempts - 1:
                continue  # try again
            # final attempt also failed — return the fallback
            return {
                "research_problem": "Extraction failed",
                "method_used": "Extraction failed",
                "dataset": "Extraction failed",
                "algorithm": "Extraction failed",
                "results": "Extraction failed",
                "advantage": "Extraction failed",
                "limitation": "Extraction failed",
                "future_scope": "Extraction failed",
            }

    return data
MAX_INPUT_CHARS = 8000  # roughly 2000 tokens — safe margin for prompt + response within Groq free tier

def prepare_text_for_extraction(raw_text: str, sections: dict = None) -> str:
    """Choose the best available text and keep it within a safe size for the LLM."""
    if sections:
        # Prefer combining the most informative sections if we have them
        priority_keys = ["abstract", "introduction", "methodology", "method", "results", "conclusion"]
        combined = "\n\n".join(sections[k] for k in priority_keys if k in sections)
        if len(combined) > 200:  # only use this if it actually captured meaningful content
            text = combined
        else:
            text = raw_text
    else:
        text = raw_text

    return text[:MAX_INPUT_CHARS]
SUMMARY_PROMPT_TEMPLATE = """Based on the following structured research paper data, write a concise 3-4 sentence narrative summary that flows naturally as a paragraph (not bullet points). Do not repeat field labels — write it as if explaining the paper to a fellow student.

Research Problem: {research_problem}
Method Used: {method_used}
Dataset: {dataset}
Algorithm: {algorithm}
Results: {results}
Advantage: {advantage}
Limitation: {limitation}
Future Scope: {future_scope}

Narrative summary:"""


def generate_narrative_summary(fields: dict) -> str:
    """Turn the 8 extracted fields into a readable paragraph summary."""
    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        research_problem=fields.get("research_problem", "Not specified"),
        method_used=fields.get("method_used", "Not specified"),
        dataset=fields.get("dataset", "Not specified"),
        algorithm=fields.get("algorithm", "Not specified"),
        results=fields.get("results", "Not specified"),
        advantage=fields.get("advantage", "Not specified"),
        limitation=fields.get("limitation", "Not specified"),
        future_scope=fields.get("future_scope", "Not specified"),
    )
    summary = ask_llm(prompt, max_tokens=300)
    return summary.strip()