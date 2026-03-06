"""
SHAP-based explainability layer for credit scoring.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from backend.config import settings
from backend.core.ml.credit_scorer import CreditScoringModel
from backend.schemas.credit import Explanation


class CreditExplainer:
    """
    Generate human-readable decision narratives and feature contribution maps.
    """

    def __init__(self, scorer: CreditScoringModel) -> None:
        self.scorer = scorer

    def shap_values(self, features: Dict[str, float]) -> Dict[str, float]:
        # Keep demo runtime deterministic: heavy SHAP can be opt-in.
        enable_shap = str(getattr(settings, "research_mode", "mock")).lower() == "live"
        if not enable_shap:
            return {k: float(v) * 0.01 for k, v in features.items()}

        artifacts = self.scorer._load_or_train()
        X = pd.DataFrame([features], columns=self.scorer.feature_order)

        try:
            import shap

            explainer = shap.TreeExplainer(artifacts.classifier)
            shap_raw = explainer.shap_values(X)
            if isinstance(shap_raw, list):
                values = shap_raw[1][0]  # class-1 contributions
            else:
                values = shap_raw[0]
            return {
                feature: float(value)
                for feature, value in zip(self.scorer.feature_order, values)
            }
        except Exception:
            # Lightweight deterministic fallback if SHAP backend is unavailable.
            return {k: float(v) * 0.01 for k, v in features.items()}

    def generate_explanation(self, features: Dict[str, float]) -> Explanation:
        shap_map = self.shap_values(features)
        ranked = sorted(shap_map.items(), key=lambda kv: abs(kv[1]), reverse=True)
        positives = [f for f in ranked if f[1] >= 0][:3]
        negatives = [f for f in ranked if f[1] < 0][:3]

        top_positive_factors = [self._factor_text(name, value, positive=True) for name, value in positives]
        top_negative_factors = [self._factor_text(name, value, positive=False) for name, value in negatives]

        narrative = self._narrative(features, top_positive_factors, top_negative_factors)
        confidence = max(0.5, min(0.95, self._completeness(features)))

        return Explanation(
            top_positive_factors=top_positive_factors,
            top_negative_factors=top_negative_factors,
            decision_narrative=narrative,
            shap_waterfall_data={k: round(v, 4) for k, v in ranked},
            confidence_in_decision=round(confidence, 2),
        )

    @staticmethod
    def _factor_text(feature: str, contribution: float, *, positive: bool) -> str:
        pretty = feature.replace("_", " ").title()
        if positive:
            return f"{pretty} supports credit quality (impact {contribution:+.3f})."
        return f"{pretty} weakens credit quality (impact {contribution:+.3f})."

    @staticmethod
    def _narrative(features: Dict[str, float], positives: List[str], negatives: List[str]) -> str:
        dscr = features.get("dscr", 1.0)
        gst_gap = features.get("gstr3b_vs_2a_itc_gap", 0.0)
        capacity = features.get("factory_capacity_utilization", 60.0)
        return (
            "The recommendation balances cashflow resilience against detected governance and compliance risks. "
            f"DSCR is observed at {dscr:.2f}x, GST ITC gap at {gst_gap:.2f}%, and factory utilization at {capacity:.1f}%. "
            "Positive drivers include: "
            + ("; ".join(positives) if positives else "limited strong positives.")
            + " Key constraints include: "
            + ("; ".join(negatives) if negatives else "no major negatives identified.")
            + " Final recommendation therefore applies risk-adjusted exposure and pricing."
        )

    @staticmethod
    def _completeness(features: Dict[str, float]) -> float:
        vals = list(features.values())
        if not vals:
            return 0.5
        non_zero = sum(1 for v in vals if abs(v) > 1e-9)
        return non_zero / len(vals)
