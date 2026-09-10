from difflib import SequenceMatcher

def compute_similarity(text_a: str, text_b: str) -> float:
    """Returns a similarity score between 0 and 1 based on text overlap."""
    score = SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()
    return round(score, 3)


def compute_pairwise_similarity(papers_data: list[dict]) -> list[dict]:
    """Compute similarity scores between every pair of papers being compared."""
    results = []
    for i in range(len(papers_data)):
        for j in range(i + 1, len(papers_data)):
            paper_a = papers_data[i]
            paper_b = papers_data[j]

            text_a = f"{paper_a.get('research_problem', '')} {paper_a.get('method_used', '')}"
            text_b = f"{paper_b.get('research_problem', '')} {paper_b.get('method_used', '')}"

            score = compute_similarity(text_a, text_b)

            results.append({
                "paper_a": paper_a["title"] or paper_a["filename"],
                "paper_b": paper_b["title"] or paper_b["filename"],
                "similarity_score": score
            })

    return results