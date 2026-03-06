"""
Node 4: Web Research Agent (with severity pre-classifier integration)
Autonomously researches the company across multiple sources using the
research fallback chain, then classifies findings by severity.

All research calls go through research_fallback_chain.py (never direct).
All LLM calls go through llm_call() (never direct Gemini/OpenAI).
"""

import logging
from typing import Dict, List

from backend.agents.state import CreditAppraisalState
from backend.agents.llm.llm_client import llm_call
from backend.agents.tools.research_fallback_chain import (
    fetch_company_news,
    fetch_promoter_background,
    fetch_mca_data,
    fetch_litigation,
    fetch_rbi_alerts,
)
from backend.agents.tools.severity_classifier import (
    classify_news,
    classify_litigation,
    classify_mca_data,
    aggregate_severity,
)

logger = logging.getLogger(__name__)


def research_agent_node(state: CreditAppraisalState) -> CreditAppraisalState:
    """
    Web research node with severity pre-classifier.
    Calls all 5 research sources, classifies severity, builds LLM explanation.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with research results and severity summary.
    """
    state["log"].append("[Research] Starting web research...")

    company = state["company_name"]
    sector = state.get("extracted_financials", {}).get("sector", "manufacturing")
    red_flags: List[str] = []
    all_severity_tags = []

    # ── 1. News Research ─────────────────────────────────────────────
    state["log"].append(f"[Research] Searching news for: {company}")
    try:
        news_results = fetch_company_news(company, sector)
        if isinstance(news_results, dict):
            news_text = news_results.get("text", str(news_results))
        else:
            news_text = str(news_results)
        state["news_summary"] = news_text

        # Classify news severity
        news_tags = classify_news(news_text)
        all_severity_tags.extend(news_tags)
    except Exception as e:
        logger.error(f"[Research] News fetch failed: {e}")
        state["news_summary"] = ""
        state["errors"].append(f"[Research] News failed: {e}")

    # ── 2. MCA21 Research ────────────────────────────────────────────
    state["log"].append(f"[Research] Fetching MCA21 data for: {company}")
    try:
        mca_data = fetch_mca_data(company)
        if isinstance(mca_data, dict):
            state["mca_data"] = mca_data
        else:
            state["mca_data"] = {}

        # Classify MCA severity
        mca_tags = classify_mca_data(state["mca_data"])
        all_severity_tags.extend(mca_tags)
    except Exception as e:
        logger.error(f"[Research] MCA fetch failed: {e}")
        state["mca_data"] = {}
        state["errors"].append(f"[Research] MCA failed: {e}")

    # ── 3. Litigation Research ───────────────────────────────────────
    state["log"].append(f"[Research] Searching litigation for: {company}")
    try:
        litigation = fetch_litigation(company)
        if isinstance(litigation, list):
            state["litigation_data"] = litigation
        else:
            state["litigation_data"] = []

        # Classify litigation severity
        lit_tags = classify_litigation(state["litigation_data"])
        all_severity_tags.extend(lit_tags)
    except Exception as e:
        logger.error(f"[Research] Litigation fetch failed: {e}")
        state["litigation_data"] = []
        state["errors"].append(f"[Research] Litigation failed: {e}")

    # ── 4. RBI Regulatory Alerts ─────────────────────────────────────
    state["log"].append("[Research] Checking RBI/SEBI regulatory alerts")
    try:
        rbi_flags = fetch_rbi_alerts(sector)
        if isinstance(rbi_flags, list):
            state["rbi_regulatory_flags"] = rbi_flags
        else:
            state["rbi_regulatory_flags"] = []
    except Exception as e:
        logger.error(f"[Research] RBI fetch failed: {e}")
        state["rbi_regulatory_flags"] = []
        state["errors"].append(f"[Research] RBI failed: {e}")

    # ── 5. Promoter Background ───────────────────────────────────────
    directors = state.get("extracted_financials", {}).get("directors", [])
    promoter_bg = {}
    for director in directors[:3]:
        try:
            bg_result = fetch_promoter_background(director, company)
            bg_text = str(bg_result)
            if any(w in bg_text.lower() for w in ["fraud", "arrested", "wilful defaulter", "lookout", "red"]):
                red_flags.append(f"Promoter alert: {director} — negative news found")
                promoter_bg[director] = "RED"
            else:
                promoter_bg[director] = "CLEAR"
        except Exception as e:
            logger.warning(f"[Research] Promoter check failed for {director}: {e}")
            promoter_bg[director] = "UNKNOWN"

    state["promoter_background"] = promoter_bg

    # ── Aggregate Severity ───────────────────────────────────────────
    severity_summary = aggregate_severity(all_severity_tags)
    state["severity_summary"] = severity_summary

    # Build red flags from severity tags
    for tag_data in severity_summary.get("all_tags", []):
        if tag_data["severity"] in ("CRITICAL", "HIGH"):
            red_flags.append(f"[{tag_data['severity']}] {tag_data['label']}: {tag_data['detail']}")

    # ── LLM Explanation ──────────────────────────────────────────────
    try:
        explanation_prompt = _format_severity_for_gemini(state, severity_summary)
        explanation = llm_call(
            explanation_prompt, task="research_explanation", max_tokens=1500
        )
        # Append LLM explanation to news summary
        state["news_summary"] = (
            state.get("news_summary", "") + "\n\n--- AI Analysis ---\n" + explanation.text
        )
    except Exception as e:
        logger.warning(f"[Research] LLM explanation failed: {e}")

    # ── Inject into extracted_financials ──────────────────────────────
    financials = state.get("extracted_financials", {})
    financials["has_prior_default"] = severity_summary.get("has_prior_default", False)
    financials["has_recovery_suit"] = severity_summary.get("has_recovery_suit", False)
    financials["active_litigation_count"] = severity_summary.get("active_litigation_count", 0)
    financials["has_promoter_issue"] = severity_summary.get("has_promoter_issue", False)
    financials["promoter_red_flag"] = severity_summary.get("has_promoter_issue", False)
    financials["din_disqualified"] = state.get("mca_data", {}).get("din_disqualified", False)
    financials["charge_count"] = state.get("mca_data", {}).get("charge_count", 0)

    if state.get("rbi_regulatory_flags"):
        financials["sector_headwind"] = True

    state["extracted_financials"] = financials
    state["research_red_flags"] = red_flags
    state["current_node"] = "research_agent"
    state["log"].append(
        f"[Research] Complete — {len(red_flags)} red flags, "
        f"overall severity: {severity_summary.get('overall_severity', 'UNKNOWN')}"
    )
    return state


def _format_severity_for_gemini(state: Dict, severity_summary: Dict) -> str:
    """
    Build a prompt for the LLM to explain research findings.

    Args:
        state: Current pipeline state.
        severity_summary: Aggregated severity summary.

    Returns:
        Formatted prompt string.
    """
    tags_text = ""
    for tag in severity_summary.get("all_tags", []):
        tags_text += f"- [{tag['severity']}] {tag['label']}: {tag['detail']}\n"

    return f"""
You are a credit research analyst at a leading Indian bank.
Summarize the following research findings for the credit committee.

Company: {state.get('company_name')}
Overall Severity: {severity_summary.get('overall_severity')}
Critical Findings: {severity_summary.get('critical_count', 0)}
High Findings: {severity_summary.get('high_count', 0)}

Detailed Findings:
{tags_text}

RBI Alerts: {', '.join(state.get('rbi_regulatory_flags', [])) or 'None'}
Promoter Status: {state.get('promoter_background', {})}

Write a 3-4 paragraph analysis covering:
1. Key risk signals and their credit implications
2. Promoter integrity assessment
3. Sector and regulatory outlook
4. Overall research conclusion

Use Indian banking terminology (NPA, DRT, DSCR, CIBIL, etc.)
"""
