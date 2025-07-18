from sqlalchemy import Column, Integer, String, JSON, DateTime, func, ForeignKey 
from .database import Base

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    parent_job_id = Column(Integer, ForeignKey("scrape_jobs.id"), nullable=True) 

    website_url = Column(String(255), index=True)
    status = Column(String(50), default="PENDING")
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), onupdate=func.now())