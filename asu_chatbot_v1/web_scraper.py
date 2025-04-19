# web_scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_page(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except:
        return ""

def get_all_documents() -> list[str]:
    urls = [
        "https://tutoring.asu.edu/writing-centers",
        "https://tutoring.asu.edu/graduate-writing-centers",
        "https://tutoring.asu.edu/expanded-writing-support",
        "https://libguides.asu.edu/designresources/citing",
        "https://libguides.asu.edu/c.php?g=264286&p=1763856",
        "https://libguides.asu.edu/c.php?g=263905&p=6112359"
    ]
    return [scrape_page(url) for url in urls]
