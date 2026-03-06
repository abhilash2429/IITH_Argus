"""
Five Cs scoring helper for CAM generation and dashboard.
"""

from __future__ import annotations

from typing import Dict


def analyze_five_cs(features: Dict[str, float]) -> Dict[str, Dict[str, object]]:
    """
    Convert feature vector to Character/Capacity/Capital/Collateral/Conditions scores.
    """
    character = 10 - min(
        10,
        (features.get("has_promoter_fraud_news", 0) * 4)
        + (features.get("has_mca_struck_off_associates", 0) * 3)
        + (features.get("management_integrity_score", 5) < 5) * 2,
    )
    capacity = min(
        10,
        max(
            1,
            (features.get("dscr", 1.0) * 3)
            + (features.get("interest_coverage_ratio", 1.0))
            + (features.get("factory_capacity_utilization", 60) / 20),
        ),
    )
    capital = min(
        10,
        max(1, 9 - features.get("debt_equity_ratio", 1.5) + features.get("current_ratio", 1.3)),
    )
    collateral = min(
        10,
        max(
            1,
            (features.get("collateral_coverage_ratio", 1.0) * 4)
            + (features.get("collateral_type_score", 5) / 2),
        ),
    )
    conditions = min(
        10,
        max(
            1,
            8
            - (features.get("has_sector_headwinds", 0) * 2.5)
            - (features.get("has_revenue_inflation_signals", 0) * 2.0),
        ),
    )

    def with_level(score: float) -> Dict[str, object]:
        if score >= 7.5:
            level = "LOW"
        elif score >= 5.0:
            level = "MEDIUM"
        else:
            level = "HIGH"
        return {"score": round(float(score), 2), "risk_level": level}

    return {
        "character": with_level(character),
        "capacity": with_level(capacity),
        "capital": with_level(capital),
        "collateral": with_level(collateral),
        "conditions": with_level(conditions),
    }

