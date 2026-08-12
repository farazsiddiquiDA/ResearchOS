from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models.paper import Paper

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    test_paper = Paper(filename="test.pdf", status="pending", title="Test Paper", authors="Test Author")
    db.add(test_paper)
    db.commit()
    db.refresh(test_paper)
    return {"inserted_id": test_paper.id, "filename": test_paper.filename}