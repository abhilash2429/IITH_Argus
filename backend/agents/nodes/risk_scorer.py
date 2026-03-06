"""
Node 6: Hybrid Risk Scorer
Applies the three-layer scoring engine:
  Layer 1: Deterministic rules (rules_engine.py)
  Layer 2: XGBoost ML calibration (ml_calibrator.py)
  Layer 3: Score blending + SHAP explainability

Qualitative adjustments from HITL are applied before scoring.
"""

import logging

from backend.agents.state import CreditAppraisalState
from backend.scoring.rules_engine import apply_rules
from backend.scoring.ml_calibrator import predict_stress_probability
from backend.scoring.shap_explainer import compute_shap_values
from backend.scoring.score_blender import (
    blend_scores,
    compute_loan_limit,
    determine_decision,
    INTEREST_PREMIUMS_BPS,
)

logger = logging.getLogger(__name__)


def risk_scorer_node(state: CreditAppraisalState) -> CreditAppraisalState:
    """
    Hybrid risk scoring node — rules + ML + SHAP.
    Applies qualitative adjustments before scoring.

    Args:
        state: Current pipeline state with financials and research.

    Returns:
        Updated state with all scoring fields populated.
    """
    state["log"].append("[Scorer] Starting hybrid risk scoring...")

    financials = state.get("extracted_financials", {})

    # Apply qualitative adjustments from HITL
    if state.get("site_visit_capacity_pct") is not None:
        financials["factory_capacity_pct"] = state["site_visit_capacity_pct"]
        state["log"].append(
            f"[Scorer] Applied site visit capacity: {state['site_visit_capacity_pct']}%"
        )

    # Inject GST reconciliation results into financials
    financials["gst_bank_mismatch_pct"] = state.get("gst_bank_mismatch_pct", 0)
    financials["circular_trading_detected"] = state.get("circular_trading_detected", False)
    financials["bounced_cheques"] = financials.get("bank", {}).get("bounced_cheques", 0)

    state["extracted_financials"] = financials

    # Layer 1: Rules engine
    rule_score, violations, strengths, critical_hit = apply_rules(financials)
    state["rule_based_score"] = rule_score
    state["rule_violations"] = state.get("rule_violations", []) + violations
    state["risk_strengths"] = strengths
    state["critical_hit"] = critical_hit

    state["log"].append(
        f"[Scorer] Rules — Score: {rule_score}/100, "
        f"Violations: {len(violations)}, Critical: {critical_hit}"
    )

    # Layer 2: ML calibration
    ml_prob = predict_stress_probability(financials)
    state["ml_stress_probability"] = ml_prob
    state["log"].append(f"[Scorer] ML stress probability: {ml_prob:.3f}")

    # Layer 3: Score blending
    final_score, risk_category = blend_scores(rule_score, ml_prob)
    state["final_risk_score"] = final_score
    state["risk_category"] = risk_category

    # SHAP explainability
    shap_vals = compute_shap_values(financials)
    state["shap_values"] = shap_vals

    # Decision
    decision = determine_decision(risk_category, critical_hit)
    state["decision"] = decision

    # Loan limit
    loan_limit = compute_loan_limit(financials, final_score)
    state["recommended_loan_limit_crore"] = loan_limit

    # Interest premium
    premium = INTEREST_PREMIUMS_BPS.get(risk_category)
    state["interest_rate_premium_bps"] = premium

    # Decision rationale
    rationale_parts = [f"Decision: {decision}"]
    rationale_parts.append(f"Final Risk Score: {final_score}/100 ({risk_category} risk)")
    if critical_hit:
        rationale_parts.append("CRITICAL rule violations triggered — auto-escalated")
    if violations:
        rationale_parts.append(f"Key violations: {'; '.join(violations[:3])}")
    if strengths:
        rationale_parts.append(f"Strengths: {'; '.join(strengths[:2])}")
    state["decision_rationale"] = ". ".join(rationale_parts)

    state["current_node"] = "risk_scorer"
    state["log"].append(
        f"[Scorer] Final — Score: {final_score}/100, Category: {risk_category}, "
        f"Decision: {decision}, Limit: ₹{loan_limit} Cr"
    )
    return state
