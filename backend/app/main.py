from fastapi import FastAPI
from app.database import get_db, engine, Base
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData
from app.routers import upload, extract, papers, analyze

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(papers.router)
app.include_router(analyze.router)

@app.get("/")
def health_check():
    return {"status": "ok"}