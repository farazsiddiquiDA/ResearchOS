from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData
from app.services.export_service import generate_paper_excel

router = APIRouter()

@router.get("/papers/{paper_id}/export")
def export_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    extracted = db.query(ExtractedData).filter(ExtractedData.paper_id == paper_id).first()
    if not extracted:
        raise HTTPException(status_code=404, detail="No extracted data yet — run /analyze first")

    buffer = generate_paper_excel(paper, extracted)

    filename = f"{paper.title or paper.filename}_summary.xlsx".replace(" ", "_")

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )