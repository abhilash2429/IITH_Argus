"""
GST parsing and mismatch analytics module.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from backend.core.india_context import INDIA_CREDIT_KNOWLEDGE
from backend.schemas.credit import (
    GSTR1Data,
    GSTR2AData,
    GSTR3BData,
    MismatchReport,
    Severity,
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass
class ParsedGSTBundle:
    gstr3b: Optional[GSTR3BData] = None
    gstr1: Optional[GSTR1Data] = None
    gstr2a: Optional[GSTR2AData] = None


class GSTParser:
    """
    Parse GST returns from JSON/XML sources.
    """

    def parse_file(self, file_path: str) -> ParsedGSTBundle:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix == ".json":
            with path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            return self.parse_payload(payload)

        if suffix in {".xml"}:
            tree = ET.parse(path)
            root = tree.getroot()
            payload = self._xml_to_dict(root)
            return self.parse_payload(payload)

        raise ValueError(f"Unsupported GST file type: {suffix}")

    def parse_payload(self, payload: Dict[str, Any]) -> ParsedGSTBundle:
        doc_type = str(payload.get("return_type", payload.get("type", ""))).upper()

        if "GSTR3B" in doc_type or "GSTR-3B" in doc_type:
            return ParsedGSTBundle(gstr3b=self._parse_gstr3b(payload))
        if "GSTR1" in doc_type or "GSTR-1" in doc_type:
            return ParsedGSTBundle(gstr1=self._parse_gstr1(payload))
        if "GSTR2A" in doc_type or "GSTR-2A" in doc_type or "GSTR2B" in doc_type:
            return ParsedGSTBundle(gstr2a=self._parse_gstr2a(payload))

        # flexible fallback: infer by keys
        if {"outward_supplies", "itc_claimed"} <= set(payload.keys()):
            return ParsedGSTBundle(gstr3b=self._parse_gstr3b(payload))
        if {"invoice_sales_total", "hsn_summary"} <= set(payload.keys()):
            return ParsedGSTBundle(gstr1=self._parse_gstr1(payload))
        if {"available_itc", "vendor_purchases"} <= set(payload.keys()):
            return ParsedGSTBundle(gstr2a=self._parse_gstr2a(payload))

        raise ValueError("Unable to detect GST return type from payload")

    @staticmethod
    def _parse_gstr3b(payload: Dict[str, Any]) -> GSTR3BData:
        return GSTR3BData(
            period=str(payload.get("period", "unknown")),
            outward_supplies=_safe_float(
                payload.get("outward_supplies", payload.get("table_3_1a"))
            ),
            itc_claimed=_safe_float(payload.get("itc_claimed", payload.get("table_4a"))),
            tax_paid=_safe_float(payload.get("tax_paid", payload.get("total_tax_paid"))),
        )

    @staticmethod
    def _parse_gstr1(payload: Dict[str, Any]) -> GSTR1Data:
        return GSTR1Data(
            period=str(payload.get("period", "unknown")),
            invoice_sales_total=_safe_float(payload.get("invoice_sales_total", payload.get("sales"))),
            hsn_summary=payload.get("hsn_summary", {}) or {},
        )

    @staticmethod
    def _parse_gstr2a(payload: Dict[str, Any]) -> GSTR2AData:
        vendor = payload.get("vendor_purchases", {}) or {}
        normalized = {str(k): _safe_float(v) for k, v in vendor.items()}
        available_itc = payload.get("available_itc")
        if available_itc is None:
            available_itc = sum(normalized.values())
        return GSTR2AData(
            period=str(payload.get("period", "unknown")),
            available_itc=_safe_float(available_itc),
            vendor_purchases=normalized,
        )

    @staticmethod
    def _xml_to_dict(element: ET.Element) -> Dict[str, Any]:
        if not list(element):
            return {element.tag: element.text or ""}

        parsed: Dict[str, Any] = {}
        for child in element:
            parsed.update(GSTParser._xml_to_dict(child))
        return parsed


class GSTMismatchAnalyzer:
    """
    India-specific GST fraud detector.
    """

    def analyze(
        self,
        gstr3b: GSTR3BData,
        gstr2a: GSTR2AData,
        *,
        gstr1: Optional[GSTR1Data] = None,
        bank_credits: Optional[float] = None,
    ) -> MismatchReport:
        available = max(gstr2a.available_itc, 1.0)
        inflation_pct = max(0.0, (gstr3b.itc_claimed - available) / available)

        revenue_inflation_flag = False
        if gstr1 and bank_credits and bank_credits > 0:
            ratio = gstr1.invoice_sales_total / bank_credits
            revenue_inflation_flag = ratio > 1.3

        fraud_threshold = INDIA_CREDIT_KNOWLEDGE["gst_concepts"]["itc_fraud_threshold"]  # type: ignore[index]
        critical_threshold = INDIA_CREDIT_KNOWLEDGE["gst_concepts"]["itc_critical_threshold"]  # type: ignore[index]

        suspected_circular = bool(inflation_pct > fraud_threshold and revenue_inflation_flag)

        if inflation_pct >= critical_threshold:
            risk = Severity.CRITICAL
        elif inflation_pct >= fraud_threshold or revenue_inflation_flag:
            risk = Severity.HIGH
        elif inflation_pct >= 0.02:
            risk = Severity.MEDIUM
        else:
            risk = Severity.LOW

        explanation_parts = [
            f"ITC claimed ₹{gstr3b.itc_claimed:,.2f} vs available ₹{gstr2a.available_itc:,.2f}."
        ]
        if revenue_inflation_flag:
            explanation_parts.append(
                "GSTR-1 outward supplies appear materially higher than observed banking credits."
            )
        if suspected_circular:
            explanation_parts.append(
                "Pattern suggests possible fake invoicing / circular trading chain."
            )

        return MismatchReport(
            itc_inflation_percentage=round(inflation_pct * 100, 2),
            revenue_inflation_flag=revenue_inflation_flag,
            suspected_circular_trading=suspected_circular,
            risk_level=risk,
            explanation=" ".join(explanation_parts),
        )

