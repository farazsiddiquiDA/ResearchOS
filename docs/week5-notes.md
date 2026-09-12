# Week 5 — Summary Generation & Batch Processing

## What was built
- Narrative summary generation (LLM turns 8 fields into a readable paragraph)
- Combined `/papers/process` endpoint: upload → extract → section → analyze in one call
- Retry/backoff logic for Groq rate limits
- Excel export for individual paper summaries

## Endpoints added this week
- POST /papers/process
- POST /analyze/batch
- GET /papers/{id}/export

## Known limitations
- Groq free tier rate limits can slow down batches of 4-5 papers (mitigated with retry + delay)
- Excel export is per-paper only; multi-paper export not yet built (planned for Week 6 comparison engine)

## Testing notes
- Tested full pipeline with [X] real papers end-to-end
- Corrupt/invalid PDF handling confirmed working — doesn't crash batch