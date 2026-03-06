"""
Severity pre-classifier for research findings.
Classifies litigation, news, and MCA data into severity tags
before they reach the LLM for explanation.

This ensures structured, rule-based severity assessment that the LLM cannot override.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SeverityTag:
    """A severity classification tag for a research finding."""
    source: str          # "litigation" | "news" | "mca"
    rule_id: str         # e.g., "drt_recovery_suit"
    severity: str        # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    label: str           # Human-readable label
    detail: str          # Specific detail/evidence
    affects_score: bool  # Whether this should influence risk score
    inject_to_financials: Optional[str] = None  # Key to inject into financials dict


# ── Litigation Classification Rules ──────────────────────────────────

LITIGATION_RULES = [
    {
        "id": "drt_recovery_suit",
        "severity": "CRITICAL",
        "keywords": ["recovery", "drt", "debt recovery tribunal"],
        "label": "DRT Recovery Suit",
        "affects_score": True,
        "inject": "has_recovery_suit",
    },
    {
        "id": "nclt_insolvency",
        "severity": "CRITICAL",
        "keywords": ["insolvency", "nclt", "winding up", "liquidation", "cirp"],
        "label": "NCLT Insolvency Proceedings",
        "affects_score": True,
        "inject": "has_recovery_suit",
    },
    {
        "id": "criminal_fraud",
        "severity": "CRITICAL",
        "keywords": ["criminal", "fraud", "cheating", "forgery", "420", "ipc"],
        "label": "Criminal Fraud Case",
        "affects_score": True,
        "inject": "promoter_red_flag",
    },
    {
        "id": "sebi_enforcement",
        "severity": "HIGH",
        "keywords": ["sebi", "securities", "insider trading", "market manipulation"],
        "label": "SEBI Enforcement Action",
        "affects_score": True,
        "inject": "promoter_red_flag",
    },
    {
        "id": "tax_dispute",
        "severity": "MEDIUM",
        "keywords": ["income tax", "tax dispute", "gst dispute", "customs"],
        "label": "Tax Dispute",
        "affects_score": False,
        "inject": None,
    },
    {
        "id": "commercial_dispute",
        "severity": "LOW",
        "keywords": ["civil", "commercial", "arbitration", "breach of contract"],
        "label": "Commercial Dispute",
        "affects_score": False,
        "inject": None,
    },
]


def classify_litigation(cases: List[Dict]) -> List[SeverityTag]:
    """
    Classify litigation cases into severity tags.

    Args:
        cases: List of case dicts from research.

    Returns:
        List of SeverityTag objects.
    """
    tags = []
    for case in cases:
        case_text = (
            f"{case.get('type', '')} {case.get('court', '')} "
            f"{case.get('parties', '')} {case.get('case_number', '')}"
        ).lower()

        matched = False
        for rule in LITIGATION_RULES:
            if any(kw in case_text for kw in rule["keywords"]):
                tags.append(SeverityTag(
                    source="litigation",
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    label=rule["label"],
                    detail=f"{case.get('court', 'Unknown')} — {case.get('parties', 'Unknown')} ({case.get('status', 'unknown')})",
                    affects_score=rule["affects_score"],
                    inject_to_financials=rule.get("inject"),
                ))
                matched = True
                break

        if not matched and case.get("status") == "pending":
            tags.append(SeverityTag(
                source="litigation",
                rule_id="unclassified_pending",
                severity="LOW",
                label="Unclassified Pending Case",
                detail=f"{case.get('court', 'Unknown')} — {case.get('case_number', 'Unknown')}",
                affects_score=False,
            ))

    return tags


# ── News Classification Rules ────────────────────────────────────────

NEWS_RULES = [
    {
        "id": "npa_classification",
        "severity": "CRITICAL",
        "keywords": ["npa", "non-performing asset", "non performing asset", "classified as npa"],
        "label": "NPA Classification",
        "affects_score": True,
        "inject": "has_prior_default",
    },
    {
        "id": "wilful_defaulter",
        "severity": "CRITICAL",
        "keywords": ["wilful defaulter", "willful defaulter", "wilful default"],
        "label": "Wilful Defaulter",
        "affects_score": True,
        "inject": "promoter_red_flag",
    },
    {
        "id": "promoter_arrested",
        "severity": "CRITICAL",
        "keywords": ["arrested", "police", "ed raid", "cbi", "enforcement directorate"],
        "label": "Promoter Arrested/Raided",
        "affects_score": True,
        "inject": "promoter_red_flag",
    },
    {
        "id": "fraud_allegation",
        "severity": "HIGH",
        "keywords": ["fraud", "scam", "embezzlement", "siphoning", "diversion of funds"],
        "label": "Fraud Allegation",
        "affects_score": True,
        "inject": "promoter_red_flag",
    },
    {
        "id": "rating_downgrade",
        "severity": "HIGH",
        "keywords": ["downgrade", "rating downgrade", "credit watch", "negative outlook"],
        "label": "Rating Downgrade",
        "affects_score": True,
        "inject": None,
    },
    {
        "id": "account_stressed",
        "severity": "HIGH",
        "keywords": ["stressed account", "sma-2", "sma-1", "special mention"],
        "label": "Account Stressed",
        "affects_score": True,
        "inject": "has_prior_default",
    },
    {
        "id": "sector_headwind",
        "severity": "LOW",
        "keywords": ["headwind", "slowdown", "margin pressure", "demand decline"],
        "label": "Sector Headwind",
        "affects_score": False,
        "inject": "sector_headwind",
    },
]


def classify_news(news_text: str) -> List[SeverityTag]:
    """
    Classify news text into severity tags by splitting on "Title:" markers.

    Args:
        news_text: Raw news text with Title:/Snippet: format.

    Returns:
        List of SeverityTag objects.
    """
    tags = []
    # Split news into individual items
    items = re.split(r"(?=Title:)", news_text)

    for item in items:
        item_lower = item.lower().strip()
        if not item_lower:
            continue

        for rule in NEWS_RULES:
            if any(kw in item_lower for kw in rule["keywords"]):
                # Extract title for detail
                title_match = re.search(r"Title:\s*(.+?)(?:\n|$)", item)
                title = title_match.group(1).strip() if title_match else item[:100]

                tags.append(SeverityTag(
                    source="news",
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    label=rule["label"],
                    detail=title,
                    affects_score=rule["affects_score"],
                    inject_to_financials=rule.get("inject"),
                ))
                break  # Only match first (most severe) rule per item

    return tags


def classify_mca_data(mca_data: Dict) -> List[SeverityTag]:
    """
    Classify MCA (Ministry of Corporate Affairs) data into severity tags.

    Args:
        mca_data: Dict from MCA scraper.

    Returns:
        List of SeverityTag objects.
    """
    tags = []

    # Check DIN disqualification
    if mca_data.get("din_disqualified"):
        tags.append(SeverityTag(
            source="mca",
            rule_id="din_disqualified",
            severity="CRITICAL",
            label="Director DIN Disqualified",
            detail="One or more directors have disqualified DIN status per MCA records",
            affects_score=True,
            inject_to_financials="din_disqualified",
        ))

    # Check charge count
    charge_count = mca_data.get("charge_count", 0)
    if charge_count > 5:
        tags.append(SeverityTag(
            source="mca",
            rule_id="high_charge_count",
            severity="HIGH",
            label="High Charge Count",
            detail=f"{charge_count} charges registered — indicates heavy pledging of assets",
            affects_score=True,
        ))
    elif charge_count > 3:
        tags.append(SeverityTag(
            source="mca",
            rule_id="moderate_charge_count",
            severity="MEDIUM",
            label="Moderate Charge Count",
            detail=f"{charge_count} charges registered",
            affects_score=False,
        ))

    # Check company status
    status = mca_data.get("company_status", "").upper()
    if status in ["STRUCK OFF", "UNDER LIQUIDATION", "DORMANT"]:
        tags.append(SeverityTag(
            source="mca",
            rule_id="company_inactive",
            severity="CRITICAL",
            label=f"Company Status: {status}",
            detail=f"Company is {status} per MCA records — not eligible for credit",
            affects_score=True,
        ))

    # Check ROC compliance
    roc_status = mca_data.get("roc_compliance_status", "").upper()
    if roc_status in ["NON-COMPLIANT", "DEFAULTING"]:
        tags.append(SeverityTag(
            source="mca",
            rule_id="roc_non_compliant",
            severity="HIGH",
            label="ROC Non-Compliant",
            detail="Company has not filed mandatory ROC returns — governance concern",
            affects_score=True,
        ))

    return tags


def aggregate_severity(all_tags: List[SeverityTag]) -> Dict[str, Any]:
    """
    Aggregate all severity tags into a summary dict.

    Args:
        all_tags: Combined list of all severity tags.

    Returns:
        Dict with: has_prior_default, has_promoter_issue, overall_severity,
        critical_count, high_count, tags_by_source, all_tags.
    """
    critical_count = sum(1 for t in all_tags if t.severity == "CRITICAL")
    high_count = sum(1 for t in all_tags if t.severity == "HIGH")

    has_prior_default = any(
        t.inject_to_financials in ("has_prior_default", "has_recovery_suit")
        for t in all_tags if t.inject_to_financials
    )
    has_promoter_issue = any(
        t.inject_to_financials == "promoter_red_flag"
        for t in all_tags if t.inject_to_financials
    )

    # Determine overall severity
    if critical_count > 0:
        overall = "CRITICAL"
    elif high_count >= 2:
        overall = "HIGH"
    elif high_count == 1:
        overall = "MODERATE"
    else:
        overall = "LOW"

    # Group by source
    tags_by_source = {}
    for tag in all_tags:
        if tag.source not in tags_by_source:
            tags_by_source[tag.source] = []
        tags_by_source[tag.source].append({
            "rule_id": tag.rule_id,
            "severity": tag.severity,
            "label": tag.label,
            "detail": tag.detail,
        })

    return {
        "has_prior_default": has_prior_default,
        "has_promoter_issue": has_promoter_issue,
        "has_recovery_suit": has_prior_default,
        "overall_severity": overall,
        "critical_count": critical_count,
        "high_count": high_count,
        "active_litigation_count": sum(1 for t in all_tags if t.source == "litigation"),
        "tags_by_source": tags_by_source,
        "all_tags": [
            {"source": t.source, "rule_id": t.rule_id, "severity": t.severity,
             "label": t.label, "detail": t.detail}
            for t in all_tags
        ],
    }
