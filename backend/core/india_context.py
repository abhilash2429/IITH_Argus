"""
Domain constants and helper utilities specific to Indian corporate credit analysis.
"""

from __future__ import annotations

from typing import Dict, List


INDIA_CREDIT_KNOWLEDGE: Dict[str, object] = {
    "gst_concepts": {
        "gstr_3b": "Monthly self-assessed summary return. Filed by 20th of next month.",
        "gstr_2a": "Auto-populated purchase register from supplier filings. Cannot be manipulated.",
        "itc_fraud_threshold": 0.05,
        "itc_critical_threshold": 0.15,
    },
    "regulatory_bodies": ["RBI", "SEBI", "MCA", "NCLT", "DRT", "SARFAESI", "IBC"],
    "npa_classification": {
        "sub_standard": "Overdue > 90 days",
        "doubtful": "Overdue > 12 months",
        "loss": "Irrecoverable",
    },
    "sector_risk_weights": {
        "real_estate": 1.4,
        "nbfc": 1.3,
        "construction": 1.3,
        "textiles": 1.0,
        "agri_processing": 0.9,
        "it_services": 0.8,
        "pharma": 0.85,
        "manufacturing": 1.0,
        "other": 1.0,
    },
    "red_flag_keywords_hindi_english": [
        "benami",
        "hawala",
        "round-tripping",
        "shell company",
        "struck off",
        "cirp",
        "liquidation",
        "attachment order",
        "lookout notice",
        "money laundering",
        "pmla",
    ],
}


def sector_risk_multiplier(sector: str) -> float:
    """
    Return sector-specific risk multiplier with safe fallback.
    """
    mapping = INDIA_CREDIT_KNOWLEDGE["sector_risk_weights"]
    return float(mapping.get(sector.lower(), mapping["other"]))  # type: ignore[arg-type]


def red_flag_keywords() -> List[str]:
    """
    Return normalized red-flag keywords used in research and parser checks.
    """
    return [k.lower() for k in INDIA_CREDIT_KNOWLEDGE["red_flag_keywords_hindi_english"]]  # type: ignore[index]

