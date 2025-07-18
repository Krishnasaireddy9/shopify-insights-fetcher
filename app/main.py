from fastapi import FastAPI, Body, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from . import db_models
from .database import engine, get_db
from .models import ScrapeRequest, JobResponse, JobResult, BrandInsights
from .services.scraping_service import run_scraping_task
from .exceptions import WebsiteNotFoundException, ScrapingException

# Creating DB tables on startup
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shopify Insights Fetcher",
    description="An API to fetch and structure data from Shopify stores."
)

@app.post("/create-scrape-job", response_model=JobResponse, status_code=202)
async def create_scrape_job(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Accepts a URL and starts a scraping job in the background.
    Returns immediately with a job ID.
    """
    new_job = db_models.ScrapeJob(
        website_url=str(request.website_url),
        status="PENDING"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    background_tasks.add_task(run_scraping_task, db, new_job.id, str(request.website_url))
    
    return {
        "job_id": new_job.id,
        "website_url": new_job.website_url,
        "status": new_job.status
    }

@app.get("/results/{job_id}", response_model=JobResult)
async def get_scrape_results(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the status and result of a scraping job by its ID.
    """
    job = db.query(db_models.ScrapeJob).filter(db_models.ScrapeJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    insights_data = None
    if job.status == "COMPLETED" and job.data:
        insights_data = BrandInsights.parse_obj(job.data)

    return {
        "job_id": job.id,
        "status": job.status,
        "website_url": job.website_url,
        "data": insights_data
    }

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Shopify Insights Fetcher is running!"}