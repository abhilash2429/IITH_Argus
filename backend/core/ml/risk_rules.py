"""
Hard rejection and rule-based risk filters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    weight: str


HARD_REJECTION_RULES = [
    Rule("going_concern_doubt", "Auditor has raised Going Concern doubts", "INSTANT_REJECT"),
    Rule("active_nclt", "Company under active NCLT/CIRP proceedings", "INSTANT_REJECT"),
    Rule("promoter_fraud_confirmed", "Promoter has confirmed fraud/arrest news", "INSTANT_REJECT"),
    Rule("severe_gst_mismatch", "GSTR-3B vs 2A ITC gap > 25%", "INSTANT_REJECT"),
]


def evaluate_hard_rules(features: Dict[str, float]) -> List[str]:
    hits: List[str] = []
    if features.get("has_going_concern_doubt", 0.0) >= 1.0:
        hits.append("going_concern_doubt")
    if features.get("has_nclt_proceedings", 0.0) >= 1.0:
        hits.append("active_nclt")
    if features.get("has_promoter_fraud_news", 0.0) >= 1.0:
        hits.append("promoter_fraud_confirmed")
    if features.get("gstr3b_vs_2a_itc_gap", 0.0) > 25.0:
        hits.append("severe_gst_mismatch")
    return hits

