"""
Research fallback chain: Primary → Grok → Stale Cache → Mock.
All research calls from nodes MUST go through these public functions.
Never call Serper, Grok, or scrapers directly from LangGraph nodes.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from backend.agents.tools.research_mode import load_from_cache, save_to_cache
from backend.agents.tools.mock_responses import (
    mock_serper_news,
    mock_serper_promoter,
    mock_mca21,
    mock_ecourts,
    mock_rbi_alerts,
)
from backend.agents.tools.serper_tool import search_news as _serper_news
from backend.agents.tools.serper_tool import search_promoter as _serper_promoter
from backend.agents.tools.mca_scraper import scrape_mca21 as _scrape_mca21
from backend.agents.tools.ecourts_scraper import search_ecourts as _search_ecourts
from backend.agents.tools.rbi_scraper import get_rbi_alerts as _get_rbi_alerts
from backend.agents.tools.grok_research_tool import (
    grok_search_news,
    grok_search_promoter,
    grok_get_mca_info,
    grok_search_litigation,
    grok_get_rbi_alerts,
)

logger = logging.getLogger(__name__)


def _try_or_fallback(
    source_name: str,
    cache_key: str,
    primary_fn: Callable,
    grok_fn: Optional[Callable],
    mock_fn: Callable,
    *args: Any,
) -> Any:
    """
    4-tier fallback chain: Primary → Grok → Stale Cache → Mock.

    Args:
        source_name: Research source identifier for caching.
        cache_key: Cache key for the query.
        primary_fn: Primary research function to try first.
        grok_fn: Grok-based fallback function (may be None).
        mock_fn: Mock function as last resort.
        *args: Arguments to pass to the functions.

    Returns:
        Research result from whichever tier succeeds.
    """
    # Tier 1: Primary source
    try:
        result = primary_fn(*args)
        if result and result != {} and result != []:
            save_to_cache(source_name, cache_key, 
                         result if isinstance(result, dict) else {"data": result})
            return result
    except Exception as e:
        logger.warning(f"[Fallback] Primary {source_name} failed: {e}")

    # Tier 2: Grok fallback
    if grok_fn:
        try:
            result = grok_fn(*args)
            if result and result != {} and result != []:
                save_to_cache(source_name, cache_key,
                             result if isinstance(result, dict) else {"data": result})
                return result
        except Exception as e:
            logger.warning(f"[Fallback] Grok {source_name} failed: {e}")

    # Tier 3: Stale cache
    cached = load_from_cache(source_name, cache_key)
    if cached is not None:
        logger.info(f"[Fallback] Using stale cache for {source_name}/{cache_key}")
        return cached.get("data", cached) if "data" in cached else cached

    # Tier 4: Mock
    logger.warning(f"[Fallback] Using mock for {source_name}/{cache_key}")
    return mock_fn(*args)


def fetch_company_news(company_name: str, sector: str) -> str:
    """
    Fetch company news through the fallback chain.

    Args:
        company_name: Company name to search.
        sector: Industry sector.

    Returns:
        News results string.
    """
    query = f"{company_name} fraud default NPA litigation RBI"
    return _try_or_fallback(
        "news", company_name,
        lambda *a: _serper_news(query),
        lambda *a: grok_search_news(company_name, sector),
        lambda *a: mock_serper_news(query),
        company_name, sector,
    )


def fetch_promoter_background(director_name: str, company_name: str) -> str:
    """
    Fetch promoter/director background through the fallback chain.

    Args:
        director_name: Director name.
        company_name: Associated company name.

    Returns:
        Background check results string.
    """
    return _try_or_fallback(
        "promoter", director_name,
        lambda *a: _serper_promoter(director_name),
        lambda *a: grok_search_promoter(director_name, company_name),
        lambda *a: mock_serper_promoter(director_name),
        director_name, company_name,
    )


def fetch_mca_data(company_name: str) -> Dict:
    """
    Fetch MCA21 company data through the fallback chain.

    Args:
        company_name: Company name.

    Returns:
        Dict with MCA registration data.
    """
    return _try_or_fallback(
        "mca21", company_name,
        lambda *a: _scrape_mca21(company_name),
        lambda *a: grok_get_mca_info(company_name),
        lambda *a: mock_mca21(company_name),
        company_name,
    )


def fetch_litigation(company_name: str) -> List[Dict]:
    """
    Fetch litigation data through the fallback chain.

    Args:
        company_name: Company name.

    Returns:
        List of case dicts.
    """
    return _try_or_fallback(
        "litigation", company_name,
        lambda *a: _search_ecourts(company_name),
        lambda *a: grok_search_litigation(company_name),
        lambda *a: mock_ecourts(company_name),
        company_name,
    )


def fetch_rbi_alerts(sector: str) -> List[str]:
    """
    Fetch RBI regulatory alerts through the fallback chain.

    Args:
        sector: Industry sector.

    Returns:
        List of alert strings.
    """
    return _try_or_fallback(
        "rbi", sector,
        lambda *a: _get_rbi_alerts(sector),
        lambda *a: grok_get_rbi_alerts(sector),
        lambda *a: mock_rbi_alerts(sector),
        sector,
    )
