import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData
from app.services.pdf_service import extract_text, split_into_sections, extract_basic_metadata
from app.services.extraction_service import prepare_text_for_extraction, extract_fields_from_text, generate_narrative_summary

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILES = 5


@router.post("/papers/process")
def process_papers(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Max {MAX_FILES} files per upload")

    results = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append({"filename": file.filename, "error": "Only PDF files are allowed"})
            continue

        try:
            # Step 1: Save file
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Step 2: Create paper row
            paper = Paper(filename=file.filename, status="pending")
            db.add(paper)
            db.commit()
            db.refresh(paper)

            # Step 3: Extract text
            text = extract_text(file_path)
            if not text or len(text) < 20:
                paper.status = "failed"
                db.commit()
                results.append({"paper_id": paper.id, "filename": file.filename, "error": "No readable text found"})
                continue

            sections = split_into_sections(text)
            metadata = extract_basic_metadata(text)

            paper.raw_text = text
            paper.sections = sections
            paper.title = metadata["title"]
            paper.status = "sectioned"
            db.commit()

            # Step 4: Run LLM analysis
            input_text = prepare_text_for_extraction(text, sections)
            fields = extract_fields_from_text(input_text)
            narrative = generate_narrative_summary(fields)

            record = ExtractedData(
                paper_id=paper.id,
                research_problem=fields.get("research_problem"),
                method_used=fields.get("method_used"),
                dataset=fields.get("dataset"),
                algorithm=fields.get("algorithm"),
                results=fields.get("results"),
                advantage=fields.get("advantage"),
                limitation=fields.get("limitation"),
                future_scope=fields.get("future_scope"),
                narrative_summary=narrative,
            )
            db.add(record)

            paper.status = "analyzed"
            db.commit()

            results.append({
                "paper_id": paper.id,
                "filename": file.filename,
                "title": paper.title,
                "status": "analyzed",
                "narrative_summary": narrative
            })

        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})

    return {"processed": results}