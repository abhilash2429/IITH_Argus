"""
ITR parser for structured tax return signals.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ITRParser:
    """
    Parse simplified ITR JSON payload and extract key financial metrics.
    """

    def parse(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if path.suffix.lower() != ".json":
            raise ValueError("ITR parser currently expects JSON input")

        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        gross_revenue = self._safe_float(payload.get("gross_revenue", payload.get("turnover")))
        taxable_income = self._safe_float(payload.get("taxable_income"))
        tax_paid = self._safe_float(payload.get("tax_paid"))
        depreciation = self._safe_float(payload.get("depreciation"))
        pan = str(payload.get("pan", "")).upper() or None
        assessment_year = str(payload.get("assessment_year", "unknown"))

        return {
            "assessment_year": assessment_year,
            "gross_revenue": gross_revenue,
            "taxable_income": taxable_income,
            "tax_paid": tax_paid,
            "depreciation": depreciation,
            "pan": pan,
        }

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            if isinstance(value, str):
                value = value.replace(",", "").strip()
            return float(value)
        except (TypeError, ValueError):
            return default

