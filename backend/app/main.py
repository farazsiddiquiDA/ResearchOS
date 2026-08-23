from fastapi import FastAPI
from app.database import get_db, engine, Base
from app.models.paper import Paper
from app.routers import upload, extract

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(upload.router)
app.include_router(extract.router)

@app.get("/")
def health_check():
    return {"status": "ok"}