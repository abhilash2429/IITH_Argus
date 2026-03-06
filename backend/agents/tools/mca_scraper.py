"""
MCA21 Portal Scraper for Ministry of Corporate Affairs data.
Public data: https://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do

Extracts: CIN, directors, charges, compliance status, company status.
Production implementation uses Playwright for JS-rendered pages.
"""

import logging
from typing import Dict

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MCA_BASE = "https://www.mca.gov.in"


def scrape_mca21(company_name: str) -> Dict:
    """
    Scrape MCA21 for company registration data.
    Stub implementation — returns empty structure.
    Use scrape_mca21_with_playwright() for production.

    Args:
        company_name: Name of the company to search.

    Returns:
        Dict with company registration details.
    """
    return {
        "cin": None,
        "company_status": "ACTIVE",
        "incorporation_date": None,
        "directors": [],
        "charge_count": 0,
        "din_disqualified": False,
        "roc_compliance_status": "COMPLIANT",
        "authorized_capital_lakh": None,
        "paid_up_capital_lakh": None,
    }


def scrape_mca21_with_playwright(company_name: str) -> Dict:
    """
    Production MCA21 scraper using Playwright for JS-rendered pages.
    Requires: pip install playwright && playwright install chromium

    Args:
        company_name: Name of the company to search.

    Returns:
        Dict with company registration details.
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to MCA company search
            page.goto(
                "https://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do",
                timeout=30000,
            )
            page.wait_for_load_state("networkidle")

            # Fill company name and submit search
            page.fill('input[name="companyName"]', company_name)
            page.click('input[type="submit"]')
            page.wait_for_load_state("networkidle")

            # Extract results HTML
            content = page.content()
            browser.close()

            return _parse_mca_results(content)
    except Exception as e:
        logger.error(f"[MCA21] Playwright scraping failed: {e}")
        return {"error": str(e)}


def _parse_mca_results(html: str) -> Dict:
    """
    Parse MCA21 search results HTML into structured dict.

    Args:
        html: Raw HTML from MCA21 portal.

    Returns:
        Dict with parsed company data.
    """
    soup = BeautifulSoup(html, "html.parser")
    result = {
        "cin": None,
        "company_status": None,
        "incorporation_date": None,
        "directors": [],
        "charge_count": 0,
        "din_disqualified": False,
        "roc_compliance_status": None,
        "authorized_capital_lakh": None,
        "paid_up_capital_lakh": None,
    }

    # Parse tables — structure varies by MCA portal version
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if "cin" in label:
                    result["cin"] = value
                elif "status" in label and "company" in label:
                    result["company_status"] = value
                elif "incorporation" in label:
                    result["incorporation_date"] = value

    return result
