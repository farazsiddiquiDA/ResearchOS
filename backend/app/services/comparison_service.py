def build_comparison_table(papers_data: list[dict]) -> dict:
    """
    Takes a list of paper dicts (each with id, title, and 8 fields)
    and reshapes them into a field-by-field comparison table.
    """
    fields = [
        "research_problem", "method_used", "dataset", "algorithm",
        "results", "advantage", "limitation", "future_scope"
    ]

    table = {}
    for field in fields:
        table[field] = {
            paper["title"] or paper["filename"]: paper.get(field, "Not specified")
            for paper in papers_data
        }

    return table
from app.services.llm_service import ask_llm

COMPARISON_INSIGHT_PROMPT = """You are comparing {n} research papers based on their extracted data below. Write a short 3-5 sentence comparative analysis highlighting key similarities, differences, and notable strengths/weaknesses across the papers. Do not repeat the raw field values verbatim — synthesize them into an insight a student could use to understand how these papers relate to each other.

{papers_summary}

Comparative analysis:"""


def generate_comparison_insight(papers_data: list[dict]) -> str:
    papers_summary = ""
    for p in papers_data:
        title = p["title"] or p["filename"]
        papers_summary += f"\n\n{title}:\n"
        papers_summary += f"- Method: {p.get('method_used', 'Not specified')}\n"
        papers_summary += f"- Algorithm: {p.get('algorithm', 'Not specified')}\n"
        papers_summary += f"- Results: {p.get('results', 'Not specified')}\n"
        papers_summary += f"- Limitation: {p.get('limitation', 'Not specified')}\n"

    prompt = COMPARISON_INSIGHT_PROMPT.format(n=len(papers_data), papers_summary=papers_summary)
    insight = ask_llm(prompt, max_tokens=400)
    return insight.strip()