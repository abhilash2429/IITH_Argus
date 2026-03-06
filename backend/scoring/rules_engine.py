"""
Layer 1: Deterministic Rule-Based Risk Engine
Encodes Indian banking underwriting logic for the Five Cs of Credit.

Rules are applied sequentially. Each rule:
  - Checks a specific condition in the financials dict
  - Assigns a score penalty (0-100 scale, 100 = best)
  - Adds a human-readable violation string if triggered
  - Critical rules (CRITICAL severity) are hard stops that force REJECT

Base score starts at 100. Rules subtract points.
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def _is_declining(revenue_list: list) -> bool:
    """
    Check if revenue shows a 3-year declining trend.

    Args:
        revenue_list: List of revenue values [year1, year2, year3] (newest first).

    Returns:
        True if consistently declining over 3 years.
    """
    if not revenue_list or len(revenue_list) < 3:
        return False
    return revenue_list[0] > revenue_list[1] > revenue_list[2]


def _compute_de_ratio(financials: dict) -> float:
    """
    Compute Debt-to-Equity ratio, capped for safety.

    Args:
        financials: Extracted financials dict.

    Returns:
        D/E ratio (capped at 999 if equity is zero/negative).
    """
    debt = financials.get("total_debt_crore") or 0
    equity = financials.get("net_worth_crore") or 1
    return debt / equity if equity > 0 else 999


# All 16 rules from the spec — exactly as defined
RULES = [
    # ── CAPACITY RULES (ability to repay) ────────────────────────────
    {
        "id": "CAP_001",
        "name": "DSCR Below 1.0",
        "severity": "CRITICAL",
        "check": lambda f: (f.get("dscr") or 999) < 1.0,
        "penalty": 40,
        "message": "DSCR below 1.0 — company cannot service debt from operations (hard stop)",
    },
    {
        "id": "CAP_002",
        "name": "DSCR Between 1.0 and 1.25",
        "severity": "HIGH",
        "check": lambda f: 1.0 <= (f.get("dscr") or 999) < 1.25,
        "penalty": 20,
        "message": "DSCR between 1.0–1.25: thin coverage margin, vulnerable to cash flow stress",
    },
    {
        "id": "CAP_003",
        "name": "EBITDA Margin Below 5%",
        "severity": "HIGH",
        "check": lambda f: (f.get("ebitda_margin_pct") or 999) < 5.0,
        "penalty": 15,
        "message": "EBITDA margin below 5% — low operational profitability",
    },
    {
        "id": "CAP_004",
        "name": "Revenue Declining 3 Years",
        "severity": "MEDIUM",
        "check": lambda f: _is_declining(f.get("revenue_crore", [])),
        "penalty": 10,
        "message": "Revenue declining for 3 consecutive years — business contraction signal",
    },
    # ── CAPITAL RULES (financial leverage) ───────────────────────────
    {
        "id": "CAP_005",
        "name": "Debt-to-Equity > 3x",
        "severity": "HIGH",
        "check": lambda f: _compute_de_ratio(f) > 3.0,
        "penalty": 20,
        "message": "Debt-to-Equity above 3x — highly leveraged balance sheet",
    },
    {
        "id": "CAP_006",
        "name": "Current Ratio Below 1.0",
        "severity": "HIGH",
        "check": lambda f: (f.get("current_ratio") or 999) < 1.0,
        "penalty": 15,
        "message": "Current ratio below 1.0 — negative working capital, liquidity risk",
    },
    {
        "id": "CAP_007",
        "name": "Negative Net Worth",
        "severity": "CRITICAL",
        "check": lambda f: (f.get("net_worth_crore") or 1) < 0,
        "penalty": 50,
        "message": "Negative net worth — company is technically insolvent (hard stop)",
    },
    # ── CHARACTER RULES (promoter integrity) ─────────────────────────
    {
        "id": "CHAR_001",
        "name": "Promoter Litigation Red Flag",
        "severity": "HIGH",
        "check": lambda f: f.get("promoter_red_flag", False),
        "penalty": 25,
        "message": "Promoter has active fraud/default news — character risk",
    },
    {
        "id": "CHAR_002",
        "name": "Director DIN Disqualified",
        "severity": "CRITICAL",
        "check": lambda f: f.get("din_disqualified", False),
        "penalty": 50,
        "message": "Director DIN disqualified by MCA — regulatory red flag (hard stop)",
    },
    {
        "id": "CHAR_003",
        "name": "Qualified Auditor Opinion",
        "severity": "HIGH",
        "check": lambda f: f.get("auditor_opinion") in ["qualified", "adverse", "disclaimer"],
        "penalty": 20,
        "message": "Auditor gave qualified/adverse opinion — financial statement reliability risk",
    },
    # ── COLLATERAL/FRAUD RULES ────────────────────────────────────────
    {
        "id": "FRAUD_001",
        "name": "Circular Trading Detected",
        "severity": "CRITICAL",
        "check": lambda f: f.get("circular_trading_detected", False),
        "penalty": 60,
        "message": "Circular GST trading pattern detected — revenue inflation suspected (hard stop)",
    },
    {
        "id": "FRAUD_002",
        "name": "GST-Bank Mismatch > 25%",
        "severity": "HIGH",
        "check": lambda f: (f.get("gst_bank_mismatch_pct") or 0) > 25,
        "penalty": 25,
        "message": "GST declared revenue and bank credits mismatch by more than 25%",
    },
    # ── LITIGATION RULES ──────────────────────────────────────────────
    {
        "id": "LIT_001",
        "name": "3 or More Active Litigations",
        "severity": "HIGH",
        "check": lambda f: (f.get("active_litigation_count") or 0) >= 3,
        "penalty": 20,
        "message": "3 or more active litigation cases — legal contingency risk",
    },
    {
        "id": "LIT_002",
        "name": "Recovery Suit / DRT Case",
        "severity": "CRITICAL",
        "check": lambda f: f.get("has_recovery_suit", False),
        "penalty": 40,
        "message": "Active recovery suit / DRT case — prior loan default indicator (hard stop)",
    },
    # ── CONDITIONS RULES (sector/macro) ──────────────────────────────
    {
        "id": "COND_001",
        "name": "Factory Capacity Below 50%",
        "severity": "MEDIUM",
        "check": lambda f: 0 < (f.get("factory_capacity_pct") or 100) < 50,
        "penalty": 15,
        "message": "Factory operating below 50% capacity — underutilization, projected cash flows adjusted",
    },
    {
        "id": "COND_002",
        "name": "Sector Regulatory Headwind",
        "severity": "LOW",
        "check": lambda f: f.get("sector_headwind", False),
        "penalty": 5,
        "message": "Active RBI/SEBI regulatory restriction on sector",
    },
]


def apply_rules(financials: dict) -> Tuple[float, List[str], List[str], bool]:
    """
    Apply all 16 rules to the financials dict.

    Args:
        financials: Extracted and consolidated financial data.

    Returns:
        Tuple of (score, violations, strengths, critical_hit).
        - score: 0-100 (100 = lowest risk)
        - violations: List of triggered rule messages
        - strengths: List of positive factor messages
        - critical_hit: True if any CRITICAL rule was triggered
    """
    score = 100.0
    violations: List[str] = []
    strengths: List[str] = []
    critical_hit = False

    for rule in RULES:
        try:
            if rule["check"](financials):
                score -= rule["penalty"]
                violations.append(f"[{rule['severity']}] {rule['message']}")
                if rule["severity"] == "CRITICAL":
                    critical_hit = True
        except Exception as e:
            logger.warning(f"[Rules] Rule {rule['id']} check failed: {e}")

    # Identify strengths
    if (financials.get("dscr") or 0) >= 1.5:
        strengths.append("Strong DSCR above 1.5x — comfortable debt servicing capacity")
    if (financials.get("current_ratio") or 0) >= 2.0:
        strengths.append("Healthy current ratio above 2.0 — good liquidity position")
    if not financials.get("circular_trading_detected"):
        strengths.append("No circular trading detected — GST transactions appear genuine")
    if financials.get("auditor_opinion") == "unqualified":
        strengths.append("Clean unqualified auditor opinion — financial statements reliable")

    return max(score, 0), violations, strengths, critical_hit
