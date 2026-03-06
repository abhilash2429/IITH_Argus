from datetime import date

from backend.core.ingestion.cross_validator import CrossValidator
from backend.schemas.credit import (
    BankStatementMetrics,
    EMIPayment,
    MismatchReport,
    Severity,
)


def test_cross_validator_flags_mismatch_and_fraud():
    bank = BankStatementMetrics(
        average_monthly_balance=12_00_000,
        abb_to_claimed_revenue_ratio=0.05,
        max_debit_single_transaction=30_00_000,
        circular_credit_debit_pairs=[],
        emi_payments=[EMIPayment(date=date(2025, 6, 1), amount=2_00_000)],
        suspected_shell_company_transfers=[],
        cash_withdrawal_pattern="NORMAL",
        year_end_window_dressing=True,
        banking_turnover=9_00_00_000,
        banking_to_gst_ratio=0.6,
    )
    gst_report = MismatchReport(
        itc_inflation_percentage=22.0,
        revenue_inflation_flag=True,
        suspected_circular_trading=True,
        risk_level=Severity.CRITICAL,
        explanation="Large mismatch",
    )

    report = CrossValidator().validate(
        gst_turnover=15_00_00_000,
        bank_metrics=bank,
        itr_data={"gross_revenue": 8_00_00_000},
        gst_mismatch=gst_report,
        annual_debt_obligation=12_00_000,
    )

    assert report.overall_data_consistency_score < 75
    assert report.fraud_indicators
    assert any("window dressing" in f.indicator.lower() for f in report.fraud_indicators)


def test_cross_validator_handles_missing_bank_metrics():
    report = CrossValidator().validate(
        gst_turnover=12_00_00_000,
        bank_metrics=None,
        itr_data={"gross_revenue": 11_50_00_000},
        gst_mismatch=None,
        annual_debt_obligation=10_00_000,
    )

    assert report.overall_data_consistency_score > 0
    assert any("bank statement unavailable" in a.title.lower() for a in report.anomalies)
    assert report.debt_service_coverage_ratio > 0
