from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    research_problem = Column(Text)
    method_used = Column(Text)
    dataset = Column(Text)
    algorithm = Column(Text)
    results = Column(Text)
    advantage = Column(Text)
    limitation = Column(Text)
    future_scope = Column(Text)
    narrative_summary = Column(Text)   # NEW
    created_at = Column(DateTime(timezone=True), server_default=func.now())