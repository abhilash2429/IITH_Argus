"""
Grok (xAI) research tool for web-grounded company research.
Uses xAI's Grok-3 model as a fallback when primary scrapers fail.
API is OpenAI-compatible with base_url="https://api.x.ai/v1".
"""

import json
import logging
from typing import Dict, List, Optional

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-3"


def _call_grok(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """
    Call xAI Grok API (OpenAI-compatible).

    Args:
        system_prompt: System-level instruction.
        user_prompt: User query.
        max_tokens: Maximum tokens in response.

    Returns:
        Generated text from Grok.

    Raises:
        RuntimeError: If API call fails.
    """
    headers = {
        "Authorization": f"Bearer {settings.grok_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }

    response = httpx.post(GROK_API_URL, json=payload, headers=headers, timeout=45)
    response.raise_for_status()

    data = response.json()
    text = data["choices"][0]["message"]["content"]
    if not text:
        raise RuntimeError("Grok returned empty response")
    return text


def grok_search_news(company_name: str, sector: str) -> str:
    """
    Use Grok to search for company news (NPA, fraud, DRT, defaults).

    Args:
        company_name: Name of the company.
        sector: Industry sector.

    Returns:
        Formatted news summary string.
    """
    system = (
        "You are an Indian corporate credit research analyst. "
        "Search for and summarize any negative news about the given company. "
        "Focus on: NPA classification, fraud allegations, DRT cases, "
        "SEBI/RBI actions, promoter arrests, wilful defaulter status."
    )
    user = (
        f"Find recent news about {company_name} in the {sector} sector in India. "
        f"Focus on any NPA, default, fraud, litigation, or regulatory action news. "
        f"Format each finding as: Title: <headline>\\nSnippet: <detail>\\n"
    )
    return _call_grok(system, user, max_tokens=1500)


def grok_search_promoter(director_name: str, company_name: str) -> str:
    """
    Use Grok to check promoter/director background.

    Args:
        director_name: Name of the director.
        company_name: Associated company name.

    Returns:
        Promoter background check result string.
    """
    system = (
        "You are an Indian corporate due diligence analyst. "
        "Check if this person has been flagged as a wilful defaulter, "
        "arrested for fraud, has SEBI/RBI actions, or is on any watchlist."
    )
    user = (
        f"Check the background of {director_name}, director of {company_name}. "
        f"Is this person a wilful defaulter? Any arrest records? "
        f"Any SEBI enforcement? Any RBI blacklisting? "
        f"Respond with: Status: CLEAR or Status: RED followed by details."
    )
    return _call_grok(system, user, max_tokens=800)


def grok_get_mca_info(company_name: str, cin: Optional[str] = None) -> Dict:
    """
    Use Grok to get MCA (Ministry of Corporate Affairs) information.

    Args:
        company_name: Name of the company.
        cin: Optional Corporate Identification Number.

    Returns:
        Dict with MCA data, includes grok_sourced=True flag.
    """
    system = (
        "You are a company registry researcher. Return ONLY valid JSON. "
        "Search for Indian company registration details from MCA/ROC records."
    )
    cin_hint = f" (CIN: {cin})" if cin else ""
    user = (
        f"Find MCA registration details for {company_name}{cin_hint}. "
        f"Return JSON with: cin, company_status, incorporation_date, "
        f"directors (list of name/din/designation), charge_count, "
        f"din_disqualified (boolean), roc_compliance_status."
    )

    try:
        text = _call_grok(system, user, max_tokens=1000)
        # Strip markdown fences
        import re
        text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
        text = re.sub(r"\n?```\s*$", "", text.strip())
        data = json.loads(text)
        data["grok_sourced"] = True
        return data
    except Exception as e:
        logger.warning(f"[Grok] MCA info parse failed: {e}")
        return {"grok_sourced": True, "error": str(e)}


def grok_search_litigation(company_name: str) -> List[Dict]:
    """
    Use Grok to search for litigation history.

    Args:
        company_name: Name of the company.

    Returns:
        List of case dicts, each with grok_sourced=True.
    """
    system = (
        "You are a legal research analyst specializing in Indian corporate litigation. "
        "Return ONLY a valid JSON array."
    )
    user = (
        f"Find court cases involving {company_name} in India. "
        f"Search DRT, NCLT, High Courts, and civil courts. "
        f"Return JSON array where each item has: case_number, court, type "
        f"(recovery/civil/criminal/insolvency), status (pending/disposed), year, parties."
    )

    try:
        text = _call_grok(system, user, max_tokens=1500)
        import re
        text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
        text = re.sub(r"\n?```\s*$", "", text.strip())
        cases = json.loads(text)
        if isinstance(cases, list):
            for case in cases:
                case["grok_sourced"] = True
            return cases
        return []
    except Exception as e:
        logger.warning(f"[Grok] Litigation parse failed: {e}")
        return []


def grok_get_rbi_alerts(sector: str) -> List[str]:
    """
    Use Grok to get RBI/SEBI regulatory alerts for a sector.

    Args:
        sector: Industry sector name.

    Returns:
        List of regulatory alert strings.
    """
    system = (
        "You are an RBI regulatory analyst. "
        "List recent RBI and SEBI circulars and advisories relevant to the given sector."
    )
    user = (
        f"What are the latest RBI and SEBI regulatory alerts, circulars, or advisories "
        f"for the {sector} sector in India? List the top 5 most relevant ones. "
        f"Format each as a single line summary."
    )

    try:
        text = _call_grok(system, user, max_tokens=800)
        alerts = [line.strip() for line in text.strip().split("\n") if line.strip()]
        return alerts[:5]
    except Exception as e:
        logger.warning(f"[Grok] RBI alerts failed: {e}")
        return []
