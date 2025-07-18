def find_competitors_for(brand_url: str) -> list[str]:
    """
    Finds competitor URLs for a given brand URL.
    In a real app, this would use a Search API. Here, we use a placeholder.
    """
    if "memy.co.in" in brand_url:
        return [
            "https://www.nykaafashion.com/",
            "https://www.ajio.com/",
            "https://www.biba.in/",
            "https://www.andindia.com/",
        ]
    # This will return an empty list if no competitors are defined for the URL
    return []