"""
RBI (Reserve Bank of India) regulatory alerts scraper.
Scrapes RBI press releases and filters by sector-relevant keywords.
Target URL: https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx
"""

import logging
from typing import List

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

RBI_PRESS_URL = "https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx"

SECTOR_KEYWORDS = {
    "textile": ["textile", "cotton", "garment", "weaving", "spinning"],
    "nbfc": ["nbfc", "non-banking", "microfinance", "housing finance"],
    "real_estate": ["real estate", "housing", "construction", "builder"],
    "steel": ["steel", "iron", "metals", "mining"],
    "fmcg": ["fmcg", "consumer goods", "retail"],
    "pharma": ["pharma", "pharmaceutical", "drug", "healthcare"],
    "it": ["information technology", "software", "digital"],
    "agriculture": ["agriculture", "crop", "farming", "agri"],
    "aviation": ["aviation", "airline", "airport"],
    "telecom": ["telecom", "spectrum", "5g"],
    "manufacturing": ["manufacturing", "industrial", "factory"],
}


def get_rbi_alerts(sector: str) -> List[str]:
    """
    Scrape RBI press releases and filter by sector keywords.

    Args:
        sector: Industry sector name.

    Returns:
        List of relevant alert strings (max 5).
    """
    try:
        response = httpx.get(RBI_PRESS_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract press release titles and links
        alerts = []
        keywords = SECTOR_KEYWORDS.get(sector.lower(), [sector.lower()])

        # Find all press release items
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                alerts.append(link.get_text(strip=True))

            if len(alerts) >= 5:
                break

        return alerts

    except Exception as e:
        logger.warning(f"[RBI] Scraping failed: {e}")
        return []
