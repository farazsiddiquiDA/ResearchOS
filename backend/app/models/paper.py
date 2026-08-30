from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    raw_text = Column(Text)
    sections = Column(JSON)          # NEW — stores the sectioned breakdown
    status = Column(String)
    title = Column(String)
    authors = Column(String)