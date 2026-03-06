"""
Cross-source financial consistency validator.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.schemas.credit import (
    Anomaly,
    BankStatementMetrics,
    CrossValidationReport,
    FraudIndicator,
    MismatchReport,
    Severity,
)


class CrossValidator:
    """
    Reconcile GST, banking, and ITR signals into one consistency score.
    """

    def validate(
        self,
        *,
        gst_turnover: float,
        bank_metrics: Optional[BankStatementMetrics] = None,
        itr_data: Optional[Dict[str, Any]] = None,
        gst_mismatch: Optional[MismatchReport] = None,
        annual_debt_obligation: float = 1.0,
        net_cash_flow: Optional[float] = None,
        receivable_days: int = 45,
        inventory_days: int = 35,
        payable_days: int = 30,
    ) -> CrossValidationReport:
        anomalies: List[Anomaly] = []
        fraud_indicators: List[FraudIndicator] = []
        recommendation_flags: List[str] = []

        has_bank_metrics = bank_metrics is not None
        bank_turnover = float(bank_metrics.banking_turnover) if bank_metrics else float(gst_turnover or 0.0)
        gst_vs_bank_gap = self._pct_gap(gst_turnover, bank_turnover)

        itr_revenue = float((itr_data or {}).get("gross_revenue", 0.0))
        itr_vs_gst_gap = self._pct_gap(itr_revenue, gst_turnover)

        if not has_bank_metrics:
            anomalies.append(
                Anomaly(
                    title="Bank statement unavailable",
                    details="Bank statement metrics missing; GST vs banking reconciliation used fallback estimates.",
                    severity=Severity.MEDIUM,
                )
            )
            recommendation_flags.append(
                "Collect at least 6-12 months of bank statements for stronger cross-validation."
            )

        if has_bank_metrics and gst_vs_bank_gap > 15:
            anomalies.append(
                Anomaly(
                    title="GST vs Banking mismatch",
                    details=f"Gap is {gst_vs_bank_gap:.2f}% between reported GST turnover and bank credits.",
                    severity=Severity.HIGH,
                )
            )
            recommendation_flags.append("Investigate revenue recognition and cash realization.")

        if itr_vs_gst_gap > 10:
            anomalies.append(
                Anomaly(
                    title="ITR vs GST mismatch",
                    details=f"Tax filing turnover differs by {itr_vs_gst_gap:.2f}%.",
                    severity=Severity.MEDIUM,
                )
            )

        if bank_metrics and bank_metrics.year_end_window_dressing:
            fraud_indicators.append(
                FraudIndicator(
                    indicator="Year-end window dressing detected",
                    source="bank_statement",
                    severity=Severity.HIGH,
                    confidence=0.82,
                )
            )
            recommendation_flags.append("Impose monthly stock and debtor statement covenant.")

        if bank_metrics and bank_metrics.circular_credit_debit_pairs:
            fraud_indicators.append(
                FraudIndicator(
                    indicator="Circular credit-debit transaction pattern",
                    source="bank_statement",
                    severity=Severity.CRITICAL,
                    confidence=0.86,
                )
            )

        if gst_mismatch and gst_mismatch.suspected_circular_trading:
            fraud_indicators.append(
                FraudIndicator(
                    indicator="GST ITC anomaly indicates potential circular trading",
                    source="gst_mismatch",
                    severity=Severity.CRITICAL,
                    confidence=0.88,
                )
            )

        effective_cash_flow = (
            net_cash_flow
            if net_cash_flow is not None
            else (bank_turnover * 0.1 if bank_turnover > 0 else max(gst_turnover, 0.0) * 0.08)
        )

        debt_service_coverage_ratio = effective_cash_flow / max(
            annual_debt_obligation, 1.0
        )
        working_capital_cycle_days = int(receivable_days + inventory_days - payable_days)

        base_score = 100.0
        base_score -= min(35.0, gst_vs_bank_gap * 0.8) if has_bank_metrics else 8.0
        base_score -= min(25.0, itr_vs_gst_gap * 0.7)
        base_score -= 20.0 if (bank_metrics and bank_metrics.year_end_window_dressing) else 0.0
        base_score -= (
            min(20.0, len(bank_metrics.circular_credit_debit_pairs) * 2.0)
            if bank_metrics
            else 0.0
        )
        if gst_mismatch and gst_mismatch.risk_level in {Severity.CRITICAL, Severity.HIGH}:
            base_score -= 15.0
        consistency_score = max(0.0, round(base_score, 2))

        if consistency_score < 55:
            recommendation_flags.append("Enhanced forensic review before sanction.")
        elif consistency_score < 75:
            recommendation_flags.append("Conditional approval with tighter monitoring.")

        return CrossValidationReport(
            gst_vs_bank_revenue_gap=round(gst_vs_bank_gap, 2),
            itr_vs_gst_revenue_gap=round(itr_vs_gst_gap, 2),
            debt_service_coverage_ratio=round(debt_service_coverage_ratio, 3),
            working_capital_cycle_days=working_capital_cycle_days,
            anomalies=anomalies,
            overall_data_consistency_score=consistency_score,
            fraud_indicators=fraud_indicators,
            recommendation_flags=recommendation_flags,
        )

    @staticmethod
    def _pct_gap(a: float, b: float) -> float:
        if a <= 0 and b <= 0:
            return 0.0
        denominator = max(abs(a), abs(b), 1.0)
        return abs(a - b) / denominator * 100
