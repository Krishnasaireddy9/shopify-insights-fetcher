class WebsiteNotFoundException(Exception):
    """Custom exception for when a website cannot be reached or does not exist."""
    pass

class ScrapingException(Exception):
    """Custom exception for errors that occur during the scraping process."""
    pass 