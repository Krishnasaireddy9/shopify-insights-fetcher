from fastapi import BackgroundTasks
from .competitor_service import find_competitors_for
from sqlalchemy.orm import Session
from .. import db_models
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

from ..models import Product, FAQItem, BrandInsights
from ..exceptions import ScrapingException
from ..utils.http_client import fetch_soup, SESSION

class ScrapingService:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.main_page_soup = fetch_soup(self.base_url)

    def get_full_insights(self) -> BrandInsights:
        """Orchestrates the scraping process and returns all insights."""
        try:
            catalog = self._fetch_product_catalog()
            
            # Now, call all the individual scraping methods
            return BrandInsights(
                website_url=self.base_url,
                product_catalog=catalog,
                social_handles=self._extract_social_handles(),
                contact_details=self._extract_contact_details(),
                faqs=self._extract_faqs(),
                important_links=self._extract_important_links(),
                privacy_policy=self._find_and_scrape_text_from_link(keywords=['privacy']),
                refund_policy=self._find_and_scrape_text_from_link(keywords=['refund', 'return']),
                brand_context=self._find_and_scrape_text_from_link(keywords=['about us', 'our story']),
                hero_products=self._extract_hero_products(catalog)
            )
        except Exception as e:
            raise ScrapingException(f"An error occurred during scraping: {e}")

    def _fetch_product_catalog(self) -> List[Product]:
        """Fetches the entire product catalog from the /products.json endpoint."""
        products_url = f"{self.base_url}/products.json"
        try:
            response = SESSION.get(products_url, timeout=10)
            response.raise_for_status()
            products_data = response.json().get("products", [])
            
            catalog = []
            for p in products_data:
                price = float(p['variants'][0].get('price', 0.0)) if p.get('variants') else 0.0
                catalog.append(Product(
                    id=p['id'], title=p['title'], vendor=p['vendor'],
                    product_type=p['product_type'], handle=p['handle'],
                    created_at=p['created_at'], price=price, variants=p['variants']
                ))
            return catalog
        except (requests.exceptions.RequestException, ValueError):
            return []

    def _extract_social_handles(self) -> Dict[str, str]:
        """Finds social media links from the homepage soup."""
        handles = {}
        social_patterns = {
            "instagram": r"instagram\.com", "facebook": r"facebook\.com",
            "twitter": r"twitter\.com", "youtube": r"youtube\.com", "tiktok": r"tiktok\.com"
        }
        for name, pattern in social_patterns.items():
            link = self.main_page_soup.find("a", href=re.compile(pattern, re.IGNORECASE))
            if link and link.get("href"):
                handles[name] = urljoin(self.base_url, link["href"])
        return handles

    def _extract_contact_details(self) -> Dict[str, List[str]]:
        """Extracts emails and phone numbers from the homepage body text."""
        body_text = self.main_page_soup.get_text(" ", strip=True)
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", body_text)
        phones = re.findall(r"(\+91[\-\s]?)?[0]?[789]\d{9}", body_text)
        return {"emails": list(set(emails)), "phones": list(set(phones))}

    def _find_and_scrape_text_from_link(self, keywords: List[str]) -> Optional[str]:
        """A helper to find a link by text and scrape the content of its page."""
        for keyword in keywords:
            link = self.main_page_soup.find("a", string=re.compile(keyword, re.IGNORECASE))
            if link and link.get("href"):
                try:
                    page_url = urljoin(self.base_url, link["href"])
                    page_soup = fetch_soup(page_url)
                    main_content = page_soup.find("main") or page_soup.find("body")
                    return main_content.get_text(separator='\n', strip=True) if main_content else None
                except Exception:
                    continue
        return None

    def _extract_faqs(self) -> List[FAQItem]:
        """Finds and extracts FAQs. This is highly heuristic."""
        faq_link = self.main_page_soup.find("a", string=re.compile("faq", re.IGNORECASE))
        if not faq_link or not faq_link.get("href"):
            return []

        try:
            faq_url = urljoin(self.base_url, faq_link["href"])
            faq_soup = fetch_soup(faq_url)
            faqs = []
            for q_tag in faq_soup.find_all(['strong', 'b']):
                question_text = q_tag.get_text(strip=True)
                answer_tag = q_tag.find_next_sibling("p")
                if question_text.endswith('?') and answer_tag:
                    faqs.append(FAQItem(question=question_text, answer=answer_tag.get_text(strip=True)))
            return faqs
        except Exception:
            return []

    def _extract_important_links(self) -> Dict[str, str]:
        """Finds common important links like 'Contact Us'."""
        links = {}
        link_keywords = ["Contact", "Track Order", "Blog"]
        for keyword in link_keywords:
            link_tag = self.main_page_soup.find("a", string=re.compile(keyword, re.IGNORECASE))
            if link_tag and link_tag.get("href"):
                links[keyword] = urljoin(self.base_url, link_tag["href"])
        return links

    def _extract_hero_products(self, catalog: List[Product]) -> List[str]:
        """Identifies products mentioned on the homepage."""
        homepage_text = self.main_page_soup.get_text().lower()
        hero_products = []
        for product in catalog:
            if product.title.lower() in homepage_text:
                hero_products.append(product.title)
        return hero_products[:5] 
    
def run_scraping_task(db: Session, job_id: int, url: str, is_competitor_scrape: bool = False):
    """
    This function is executed in the background. It performs the scrape,
    updates the database, and can trigger competitor scrapes.
    """
    try:
        service = ScrapingService(base_url=url)
        insights = service.get_full_insights()

        job = db.query(db_models.ScrapeJob).filter(db_models.ScrapeJob.id == job_id).first()
        if job:
            job.status = "COMPLETED"
            job.data = insights.dict()
            db.commit()

            # START: New Competitor Logic (Bonus)
            # Only find competitors if this is an original job,not a competitor scrape itself.
            if not is_competitor_scrape:
                competitors = find_competitors_for(url)
                for competitor_url in competitors:
                    # Create a new DB record for the competitor job
                    competitor_job = db_models.ScrapeJob(
                        website_url=competitor_url,
                        status="PENDING",
                        parent_job_id=job.id # Link it to the original job
                    )
                    db.add(competitor_job)
                    db.commit()
                    db.refresh(competitor_job)

                    # Create a background task for the new competitor job
                    # Note: We create a new BackgroundTasks object because we're already in a background task
                    background = BackgroundTasks()
                    background.add_task(run_scraping_task, db, competitor_job.id, competitor_url, is_competitor_scrape=True)
                    # This part is tricky as we can't easily start a new task from a task.
                    print(f"Would start background task for competitor job ID: {competitor_job.id} for URL: {competitor_url}")
            # END: New Competitor Logic

    except Exception as e:
        job = db.query(db_models.ScrapeJob).filter(db_models.ScrapeJob.id == job_id).first()
        if job:
            job.status = f"FAILED: {str(e)}"
            db.commit()