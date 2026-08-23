from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper

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
        "raw_text_length": len(paper.raw_text) if paper.raw_text else 0
    }

@router.get("/papers/{paper_id}/status")
def get_paper_status(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"id": paper.id, "status": paper.status}