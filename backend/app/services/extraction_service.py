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
def extract_fields_from_text(paper_text: str) -> dict:
    """Call the LLM to extract the 8 fields, parsing defensively."""
    prompt = build_extraction_prompt(paper_text)
    raw_response = ask_llm(prompt, max_tokens=800)

    cleaned = raw_response.strip()

    # Defensive cleanup: strip markdown code fences if the LLM added them anyway
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # If parsing fails, return a fallback structure so the app doesn't crash
        data = {
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