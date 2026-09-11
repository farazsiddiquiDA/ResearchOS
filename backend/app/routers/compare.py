from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData
from app.services.comparison_service import build_comparison_table, generate_comparison_insight
from app.services.similarity_service import compute_pairwise_similarity

router = APIRouter()

class CompareRequest(BaseModel):
    paper_ids: list[int]


@router.post("/compare")
def compare_papers(request: CompareRequest, db: Session = Depends(get_db)):
    if len(request.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 papers to compare")
    if len(request.paper_ids) > 5:
        raise HTTPException(status_code=400, detail="Max 5 papers per comparison")

    papers_data = []

    for paper_id in request.paper_ids:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        extracted = db.query(ExtractedData).filter(ExtractedData.paper_id == paper_id).first()
        if not extracted:
            raise HTTPException(status_code=400, detail=f"Paper {paper_id} has no extracted data — run /analyze first")

        papers_data.append({
            "id": paper.id,
            "title": paper.title,
            "filename": paper.filename,
            "research_problem": extracted.research_problem,
            "method_used": extracted.method_used,
            "dataset": extracted.dataset,
            "algorithm": extracted.algorithm,
            "results": extracted.results,
            "advantage": extracted.advantage,
            "limitation": extracted.limitation,
            "future_scope": extracted.future_scope,
        })

    comparison_table = build_comparison_table(papers_data)
    insight = generate_comparison_insight(papers_data)
    similarity_scores = compute_pairwise_similarity(papers_data)

    return {
        "papers_compared": [{"id": p["id"], "title": p["title"] or p["filename"]} for p in papers_data],
        "comparison_table": comparison_table,
        "comparative_insight": insight,
        "similarity_scores": similarity_scores
    }
from fastapi.responses import StreamingResponse
from app.services.export_service import generate_comparison_excel

@router.post("/compare/export")
def export_comparison(request: CompareRequest, db: Session = Depends(get_db)):
    if len(request.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 papers to compare")
    if len(request.paper_ids) > 5:
        raise HTTPException(status_code=400, detail="Max 5 papers per comparison")

    papers_data = []
    for paper_id in request.paper_ids:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
        extracted = db.query(ExtractedData).filter(ExtractedData.paper_id == paper_id).first()
        if not extracted:
            raise HTTPException(status_code=400, detail=f"Paper {paper_id} has no extracted data")

        papers_data.append({
            "id": paper.id,
            "title": paper.title or paper.filename,
            "research_problem": extracted.research_problem,
            "method_used": extracted.method_used,
            "dataset": extracted.dataset,
            "algorithm": extracted.algorithm,
            "results": extracted.results,
            "advantage": extracted.advantage,
            "limitation": extracted.limitation,
            "future_scope": extracted.future_scope,
        })

    comparison_table = build_comparison_table(papers_data)
    similarity_scores = compute_pairwise_similarity(papers_data)
    papers_compared = [{"id": p["id"], "title": p["title"]} for p in papers_data]

    buffer = generate_comparison_excel(papers_compared, comparison_table, similarity_scores)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=comparison_report.xlsx"}
    )