"""
SHAP Explainability for credit risk predictions.
Generates feature importance values for each prediction.
These values power the SHAP waterfall chart in the Next.js frontend.

Positive SHAP = increases stress probability (bad for credit)
Negative SHAP = decreases stress probability (good for credit)
"""

import logging
import pickle
from typing import Dict

from backend.scoring.ml_calibrator import extract_ml_features, FEATURE_NAMES

logger = logging.getLogger(__name__)


def compute_shap_values(financials: dict) -> Dict[str, float]:
    """
    Compute SHAP values for each feature in the credit prediction.
    Falls back to rule-based approximation if model/SHAP unavailable.

    Args:
        financials: Extracted financial data dict.

    Returns:
        Dict of {feature_name: shap_value} sorted by absolute importance.
    """
    try:
        import shap

        with open("ml/model/xgb_credit_model.pkl", "rb") as f:
            model = pickle.load(f)

        features = extract_ml_features(financials)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features)[0]

        result = {name: float(val) for name, val in zip(FEATURE_NAMES, shap_values)}
        # Sort by absolute value (most impactful first)
        return dict(sorted(result.items(), key=lambda x: abs(x[1]), reverse=True))

    except Exception as e:
        logger.warning(f"[SHAP] TreeExplainer failed, using rule-based fallback: {e}")
        return _rule_based_shap_approximation(financials)


def _rule_based_shap_approximation(financials: dict) -> Dict[str, float]:
    """
    Fallback: approximate SHAP values from rule contributions.

    Args:
        financials: Financial data dict.

    Returns:
        Dict of approximate SHAP values.
    """
    shap_approx = {}

    # DSCR: below 1.25 increases risk
    dscr = financials.get("dscr") or 1.25
    shap_approx["dscr"] = round(-(dscr - 1.25) * 0.5, 4)

    # EBITDA margin
    ebitda = financials.get("ebitda_margin_pct") or 10.0
    shap_approx["ebitda_margin_pct"] = round(-(ebitda - 10.0) * 0.02, 4)

    # Current ratio
    cr = financials.get("current_ratio") or 1.5
    shap_approx["current_ratio"] = round(-(cr - 1.5) * 0.15, 4)

    # D/E ratio
    debt = financials.get("total_debt_crore") or 0
    equity = financials.get("net_worth_crore") or 1
    de = debt / equity if equity > 0 else 5.0
    shap_approx["debt_to_equity"] = round((de - 2.0) * 0.1, 4)

    # Revenue growth
    shap_approx["revenue_growth_yoy"] = round(-0.05, 4)

    # GST mismatch
    mismatch = financials.get("gst_bank_mismatch_pct") or 0
    shap_approx["gst_bank_mismatch_pct"] = round(mismatch * 0.005, 4)

    # Litigation
    lit = financials.get("active_litigation_count") or 0
    shap_approx["active_litigation_count"] = round(lit * 0.05, 4)

    # Promoter red flag
    shap_approx["promoter_red_flag"] = 0.15 if financials.get("promoter_red_flag") else 0.0

    # Factory capacity
    cap = financials.get("factory_capacity_pct") or 80
    shap_approx["factory_capacity_pct"] = round((80 - cap) * 0.003, 4)

    # Auditor
    shap_approx["auditor_qualified"] = (
        0.12 if financials.get("auditor_opinion") in ["qualified", "adverse"] else 0.0
    )

    # Charges
    charges = financials.get("charge_count") or 0
    shap_approx["charge_count"] = round(charges * 0.02, 4)

    # Bounced cheques
    bounced = financials.get("bounced_cheques") or 0
    shap_approx["bounced_cheques_12m"] = round(bounced * 0.03, 4)

    # Sector risk
    shap_approx["sector_risk_index"] = round(0.02, 4)

    return dict(sorted(shap_approx.items(), key=lambda x: abs(x[1]), reverse=True))
