from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData
from app.services.extraction_service import prepare_text_for_extraction, extract_fields_from_text
from app.models.paper import Paper

router = APIRouter()

@router.post("/papers/{paper_id}/analyze")
def analyze_paper(paper_id: int, db: Session = Depends(get_db)):
    # Step A: find the paper
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.raw_text:
        raise HTTPException(status_code=400, detail="Paper has no extracted text yet — run /extract first")

    # Step B: prepare text and call the LLM
    text = prepare_text_for_extraction(paper.raw_text, paper.sections)
    fields = extract_fields_from_text(text)

    # Step C: check if extracted_data already exists for this paper (avoid duplicates)
    existing = db.query(ExtractedData).filter(ExtractedData.paper_id == paper_id).first()

    if existing:
        # Update existing row instead of creating a duplicate
        existing.research_problem = fields.get("research_problem")
        existing.method_used = fields.get("method_used")
        existing.dataset = fields.get("dataset")
        existing.algorithm = fields.get("algorithm")
        existing.results = fields.get("results")
        existing.advantage = fields.get("advantage")
        existing.limitation = fields.get("limitation")
        existing.future_scope = fields.get("future_scope")
        db.commit()
        db.refresh(existing)
        record = existing
    else:
        record = ExtractedData(
            paper_id=paper_id,
            research_problem=fields.get("research_problem"),
            method_used=fields.get("method_used"),
            dataset=fields.get("dataset"),
            algorithm=fields.get("algorithm"),
            results=fields.get("results"),
            advantage=fields.get("advantage"),
            limitation=fields.get("limitation"),
            future_scope=fields.get("future_scope"),
        )
        db.add(record)
        db.commit()
        db.refresh(record)

    # Step D: update paper status
    paper.status = "analyzed"
    db.commit()

    return {
        "paper_id": paper_id,
        "status": "analyzed",
        "extracted_data": {
            "research_problem": record.research_problem,
            "method_used": record.method_used,
            "dataset": record.dataset,
            "algorithm": record.algorithm,
            "results": record.results,
            "advantage": record.advantage,
            "limitation": record.limitation,
            "future_scope": record.future_scope,
        }
    }
@router.post("/analyze/batch")
def analyze_all_pending(db: Session = Depends(get_db)):
    """Run /analyze on every paper that has raw_text but hasn't been analyzed yet."""
    papers = db.query(Paper).filter(
        Paper.raw_text.isnot(None),
        Paper.status != "analyzed"
    ).all()

    if not papers:
        return {"message": "No papers pending analysis", "analyzed": []}

    results = []
    for paper in papers:
        try:
            text = prepare_text_for_extraction(paper.raw_text, paper.sections)
            fields = extract_fields_from_text(text)

            existing = db.query(ExtractedData).filter(ExtractedData.paper_id == paper.id).first()
            if existing:
                for key, value in fields.items():
                    setattr(existing, key, value)
            else:
                existing = ExtractedData(paper_id=paper.id, **fields)
                db.add(existing)

            paper.status = "analyzed"
            db.commit()

            results.append({"paper_id": paper.id, "filename": paper.filename, "status": "analyzed"})
        except Exception as e:
            results.append({"paper_id": paper.id, "filename": paper.filename, "status": "failed", "error": str(e)})

    return {"analyzed": results}