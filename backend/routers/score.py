"""
Score router — retrieve risk scoring results and SHAP values.
GET /score/{company_id}: Full risk score record.
GET /score/{company_id}/shap: SHAP values formatted for Recharts.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.db_models import RiskScore

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/score/{company_id}")
async def get_score(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the full risk score record for a company.

    Args:
        company_id: UUID of the company.
        db: Database session.

    Returns:
        Risk score record with all fields.
    """
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.company_id == company_id)
        .order_by(RiskScore.created_at.desc())
        .limit(1)
    )
    score = result.scalars().first()

    if not score:
        return {"error": "No score found for this company"}

    return {
        "company_id": str(score.company_id),
        "rule_based_score": score.rule_based_score,
        "ml_stress_probability": score.ml_stress_probability,
        "final_risk_score": score.final_risk_score,
        "risk_category": score.risk_category,
        "rule_violations": score.rule_violations,
        "risk_strengths": score.risk_strengths,
        "shap_values": score.shap_values,
        "decision": score.decision,
        "recommended_limit_crore": score.recommended_limit_crore,
        "interest_premium_bps": score.interest_premium_bps,
        "decision_rationale": score.decision_rationale,
    }


@router.get("/score/{company_id}/shap")
async def get_shap(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get SHAP values formatted for Recharts horizontal bar chart.

    Args:
        company_id: UUID of the company.
        db: Database session.

    Returns:
        List of {feature, value, direction} objects.
    """
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.company_id == company_id)
        .order_by(RiskScore.created_at.desc())
        .limit(1)
    )
    score = result.scalars().first()

    if not score or not score.shap_values:
        return []

    # Human-readable feature names
    feature_labels = {
        "dscr": "DSCR (Debt Service Coverage)",
        "ebitda_margin_pct": "EBITDA Margin %",
        "current_ratio": "Current Ratio",
        "debt_to_equity": "Debt/Equity Ratio",
        "revenue_growth_yoy": "Revenue Growth (YoY)",
        "gst_bank_mismatch_pct": "GST-Bank Mismatch %",
        "active_litigation_count": "Active Litigations",
        "promoter_red_flag": "Promoter Red Flag",
        "factory_capacity_pct": "Factory Capacity %",
        "auditor_qualified": "Auditor Qualified Opinion",
        "charge_count": "MCA Charge Count",
        "bounced_cheques_12m": "Bounced Cheques (12m)",
        "sector_risk_index": "Sector Risk Index",
    }

    shap_data = []
    for feature, value in score.shap_values.items():
        shap_data.append({
            "feature": feature_labels.get(feature, feature),
            "value": round(value, 4),
            "direction": "positive" if value > 0 else "negative",
        })

    # Sort by absolute value
    shap_data.sort(key=lambda x: abs(x["value"]), reverse=True)
    return shap_data
