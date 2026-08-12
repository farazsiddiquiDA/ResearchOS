# ResearchOS — API Specification

## Endpoints (Planned)

| Method | Endpoint             | Description |
|  ---   |    -------------     |     ---     |
| POST   | /upload              | Upload PDF(s) |
| GET    | /papers              | List all papers |
| GET    | /papers/{id}         | Get one paper's details |
| POST   | /papers/{id}/analyze | Run extraction on one paper |
| GET    | /papers/{id}/summary | Get a paper's structured summary |
| POST   | /compare             | Compare multiple papers |
| GET    | /papers/{id}/status  | Check processing status |

## Notes
- All endpoints return JSON.
- `/upload` accepts multipart/form-data (PDF files).
- `/compare` accepts a list of paper IDs and returns a comparison table.
- Status values for a paper: "pending" → "processing" → "processed" / "failed"