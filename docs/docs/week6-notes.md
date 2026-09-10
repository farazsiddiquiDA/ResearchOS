# Week 6 — Comparison Engine

## What was built
- POST /compare — structured field-by-field comparison table + LLM comparative insight
- Similarity scoring using sentence-transformers (all-MiniLM-L6-v2)
- POST /compare/export — Excel export of full comparison + similarity scores

## Testing notes
- Tested with 3 real papers across [topic area]
- Similarity scores ranged from X to Y — consistent with expected topic relatedness
- Edge cases (too few/many papers, missing data) handled with clear error messages