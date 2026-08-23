import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILES = 5

@router.post("/upload")
def upload_papers(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Max {MAX_FILES} files per upload")

    results = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append({"filename": file.filename, "error": "Only PDF files are allowed"})
            continue

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_paper = Paper(
            filename=file.filename,
            status="pending",
            raw_text=None,
            title=None,
            authors=None
        )
        db.add(new_paper)
        db.commit()
        db.refresh(new_paper)

        results.append({
            "id": new_paper.id,
            "filename": new_paper.filename,
            "status": new_paper.status
        })

    return {"uploaded": results}