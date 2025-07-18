import pydantic
from typing import List, Dict, Optional

# A base configuration to be shared across models
class BaseConfig(pydantic.BaseModel):
    class Config:
        from_attributes = True

class ScrapeRequest(pydantic.BaseModel):
    """Defines the structure for the incoming API request."""
    website_url: pydantic.HttpUrl

class Product(BaseConfig):
    """Represents a single product from the store's catalog."""
    id: int
    title: str
    vendor: str
    product_type: str
    handle: str
    created_at: str
    price: float
    variants: List[Dict]

class FAQItem(BaseConfig):
    """Represents a single Question & Answer pair."""
    question: str
    answer: str

class BrandInsights(BaseConfig):
    """The main response model that holds all scraped data."""
    website_url: str
    product_catalog: List[Product]
    hero_products: List[str]
    social_handles: Dict[str, str]
    contact_details: Dict[str, List[str]]
    faqs: List[FAQItem]
    important_links: Dict[str, str]
    brand_context: Optional[str] = "Context not found."
    privacy_policy: Optional[str] = "Policy not found."
    refund_policy: Optional[str] = "Policy not found."

class JobResponse(BaseConfig):
    """The response model when a new job is created."""
    job_id: int
    website_url: str
    status: str

class JobResult(BaseConfig):
    """The response model for checking a job's result."""
    job_id: int
    status: str
    website_url: str
    data: Optional[BrandInsights] = None 