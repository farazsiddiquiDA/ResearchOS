import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper
from app.services.pdf_service import extract_text

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/papers/{paper_id}/extract")
def extract_paper_text(paper_id: int, db: Session = Depends(get_db)):
    # Look up the paper
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    file_path = os.path.join(UPLOAD_DIR, paper.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    # Extract text
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

    # Save to DB
    paper.raw_text = text
    paper.status = "extracted"
    db.commit()
    db.refresh(paper)

    return {
        "id": paper.id,
        "filename": paper.filename,
        "status": paper.status,
        "text_length": len(text),
        "preview": text[:300]  # just show the first 300 chars so you can sanity-check it
    }