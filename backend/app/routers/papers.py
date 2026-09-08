from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData

router = APIRouter()


@router.get("/papers")
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).order_by(Paper.upload_date.desc()).all()
    return [
        {
            "id": p.id,
            "filename": p.filename,
            "status": p.status,
            "upload_date": p.upload_date,
            "title": p.title
        }
        for p in papers
    ]


@router.get("/papers/{paper_id}")
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {
        "id": paper.id,
        "filename": paper.filename,
        "status": paper.status,
        "upload_date": paper.upload_date,
        "title": paper.title,
        "authors": paper.authors,
        "raw_text_length": len(paper.raw_text) if paper.raw_text else 0,
        "sections_found": list(paper.sections.keys()) if paper.sections else [],
        "section_lengths": {k: len(v) for k, v in paper.sections.items()} if paper.sections else {}
    }


@router.get("/papers/{paper_id}/status")
def get_paper_status(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"id": paper.id, "status": paper.status}


@router.get("/papers/{paper_id}/summary")
def get_paper_summary(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    extracted = db.query(ExtractedData).filter(ExtractedData.paper_id == paper_id).first()
    if not extracted:
        raise HTTPException(status_code=404, detail="No extracted data yet — run /analyze first")

    return {
        "id": paper.id,
        "title": paper.title,
        "filename": paper.filename,
        "narrative_summary": extracted.narrative_summary,
        "research_problem": extracted.research_problem,
        "method_used": extracted.method_used,
        "dataset": extracted.dataset,
        "algorithm": extracted.algorithm,
        "results": extracted.results,
        "advantage": extracted.advantage,
        "limitation": extracted.limitation,
        "future_scope": extracted.future_scope,
    }