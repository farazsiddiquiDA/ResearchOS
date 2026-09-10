from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db, engine, Base
from app.models.paper import Paper
from app.models.extracted_data import ExtractedData
from app.routers import upload, extract, papers, analyze, process, export, compare

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow the React dev server to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(papers.router)
app.include_router(analyze.router)
app.include_router(process.router)
app.include_router(export.router)
app.include_router(compare.router)

@app.get("/")
def health_check():
    return {"status": "ok"}