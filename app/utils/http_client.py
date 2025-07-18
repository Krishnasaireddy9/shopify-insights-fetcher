import requests
from bs4 import BeautifulSoup

from ..exceptions import WebsiteNotFoundException

# Create a single, reusable session object to manage connections
SESSION = requests.Session()

# Set a standard User-Agent header to avoid being blocked by websites
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

def fetch_soup(url: str) -> BeautifulSoup:
    """
    Fetches content from a URL and returns a BeautifulSoup object for parsing.
    
    Raises:
        WebsiteNotFoundException: If the site cannot be reached or returns an error.
    """
    try:
        response = SESSION.get(url, timeout=15) # Set a 15-second timeout
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        return BeautifulSoup(response.content, "lxml")
    except requests.exceptions.RequestException as e:
        # Catch any request-related errors (DNS failure, connection timeout, etc.)
        # and wrap it in our custom exception.
        raise WebsiteNotFoundException(f"Failed to connect to {url}: {e}")