import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper
from app.services.pdf_service import extract_text, split_into_sections

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/papers/{paper_id}/extract")
def extract_paper_text(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    file_path = os.path.join(UPLOAD_DIR, paper.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    try:
        text = extract_text(file_path)
    except Exception as e:
        paper.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    if not text or len(text) < 20:
        paper.status = "failed"
        db.commit()
        raise HTTPException(status_code=422, detail="No readable text found in PDF")

    sections = split_into_sections(text)

    paper.raw_text = text
    paper.sections = sections
    paper.status = "sectioned"
    db.commit()
    db.refresh(paper)

    return {
        "id": paper.id,
        "filename": paper.filename,
        "status": paper.status,
        "text_length": len(text),
        "sections_found": list(sections.keys()),
        "preview": text[:300]
    }