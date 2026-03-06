"""
Layer 2: XGBoost ML Calibration
Captures nonlinear relationships between financial features.
Output: probability of credit stress (0.0 = no stress, 1.0 = definite stress).

The model does NOT make the credit decision.
It provides a calibrated probability that ADJUSTS the rule-based score.
"""

import logging
import os
import pickle
from typing import Dict

import numpy as np

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../ml/model/xgb_credit_model.pkl")

FEATURE_NAMES = [
    "dscr",
    "ebitda_margin_pct",
    "current_ratio",
    "debt_to_equity",
    "revenue_growth_yoy",
    "gst_bank_mismatch_pct",
    "active_litigation_count",
    "promoter_red_flag",         # 0 or 1
    "factory_capacity_pct",
    "auditor_qualified",         # 0 or 1
    "charge_count",
    "bounced_cheques_12m",
    "sector_risk_index",         # 0-10 scale by sector
]

SECTOR_RISK_INDEX = {
    "nbfc": 8,
    "real_estate": 7,
    "construction": 7,
    "aviation": 9,
    "telecom": 6,
    "steel": 5,
    "fmcg": 3,
    "pharma": 3,
    "it": 2,
    "manufacturing": 4,
    "agriculture": 5,
    "textile": 5,
    "other": 5,
    "energy": 4,
}


def _compute_de_ratio(financials: dict) -> float:
    """
    Compute Debt-to-Equity ratio, capped at 10.0.

    Args:
        financials: Extracted financials dict.

    Returns:
        D/E ratio, capped at 10.0.
    """
    debt = financials.get("total_debt_crore") or 0
    equity = financials.get("net_worth_crore") or 1
    return min(debt / equity if equity > 0 else 10.0, 10.0)


def extract_ml_features(financials: dict) -> np.ndarray:
    """
    Convert extracted financials dict to ML feature vector.

    Args:
        financials: Consolidated financial data dict.

    Returns:
        numpy array of shape (1, 13) with feature values.
    """
    revenue = financials.get("revenue_crore", [0, 0])
    if isinstance(revenue, list) and len(revenue) >= 2 and revenue[1]:
        revenue_growth = (revenue[0] - revenue[1]) / revenue[1]
    else:
        revenue_growth = 0.0

    features = [
        financials.get("dscr") or 1.0,
        financials.get("ebitda_margin_pct") or 0.0,
        financials.get("current_ratio") or 1.0,
        _compute_de_ratio(financials),
        revenue_growth,
        financials.get("gst_bank_mismatch_pct") or 0.0,
        financials.get("active_litigation_count") or 0,
        int(financials.get("promoter_red_flag", False)),
        financials.get("factory_capacity_pct") or 80.0,
        int(financials.get("auditor_opinion") in ["qualified", "adverse"]),
        financials.get("charge_count") or 0,
        financials.get("bounced_cheques") or 0,
        SECTOR_RISK_INDEX.get(
            str(financials.get("sector", "other")).lower(), 5
        ),
    ]
    return np.array(features, dtype=np.float64).reshape(1, -1)


def predict_stress_probability(financials: dict) -> float:
    """
    Load trained XGBoost model and predict stress probability.

    Args:
        financials: Extracted financial data dict.

    Returns:
        Float probability 0.0-1.0 (1.0 = high stress). Returns 0.5 if model not found.
    """
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        features = extract_ml_features(financials)
        prob = model.predict_proba(features)[0][1]  # probability of class 1 (stress)
        return float(prob)
    except FileNotFoundError:
        logger.warning("[ML] Model not found — returning neutral 0.5")
        return 0.5
    except Exception as e:
        logger.error(f"[ML] Prediction failed: {e}")
        return 0.5
