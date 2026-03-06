"""
Google Search via Serper API with mock/cached/live mode support.
Serper provides structured JSON results from Google Search.
Used for company news research and promoter background checks.
"""

import logging
from typing import Optional

import httpx

from backend.config import settings
from backend.agents.tools.research_mode import research_tool
from backend.agents.tools.mock_responses import mock_serper_news, mock_serper_promoter

logger = logging.getLogger(__name__)

SERPER_URL = "https://google.serper.dev/search"


def _live_search(query: str, num_results: int = 10) -> str:
    """
    Execute a live Google Search via Serper API.

    Args:
        query: Search query string.
        num_results: Number of results to return.

    Returns:
        Formatted string of search results.
    """
    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": num_results, "gl": "in", "hl": "en"}

    response = httpx.post(SERPER_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("organic", []):
        results.append(
            f"Title: {item.get('title')}\n"
            f"Snippet: {item.get('snippet')}\n"
            f"Link: {item.get('link')}"
        )
    return "\n\n".join(results)


@research_tool(source="serper", mock_fn=mock_serper_news)
def search_news(query: str) -> str:
    """
    Search for company-related news using Serper.

    Args:
        query: Company name + keywords for news search.

    Returns:
        Formatted news results string.
    """
    return _live_search(
        f"{query} site:economictimes.com OR site:livemint.com OR site:business-standard.com"
    )


@research_tool(source="serper_promoter", mock_fn=mock_serper_promoter)
def search_promoter(name: str) -> str:
    """
    Search for promoter/director background information.

    Args:
        name: Director or promoter full name.

    Returns:
        Formatted promoter background results string.
    """
    return _live_search(
        f'"{name}" fraud default SEBI RBI arrested wilful defaulter India'
    )
