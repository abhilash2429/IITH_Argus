from backend.core.ml.credit_scorer import CreditScoringModel


def test_credit_scorer_predict(tmp_path):
    model = CreditScoringModel(model_dir=str(tmp_path / "model"))
    model.train_on_synthetic_data(n_samples=200)
    features = {
        "revenue_cagr_3yr": 0.12,
        "ebitda_margin": 13.0,
        "debt_equity_ratio": 1.4,
        "current_ratio": 1.5,
        "interest_coverage_ratio": 2.1,
        "dscr": 1.45,
        "gst_banking_ratio": 0.97,
        "itr_gst_consistency_score": 88.0,
        "average_bank_balance_to_limit_ratio": 0.18,
        "has_auditor_qualification": 0.0,
        "has_going_concern_doubt": 0.0,
        "has_litigation": 0.0,
        "has_mca_struck_off_associates": 0.0,
        "has_circular_trading_signals": 0.0,
        "has_revenue_inflation_signals": 0.0,
        "has_promoter_fraud_news": 0.0,
        "has_sector_headwinds": 0.0,
        "has_nclt_proceedings": 0.0,
        "gstr3b_vs_2a_itc_gap": 2.0,
        "gst_return_filing_consistency": 95.0,
        "mca_filing_compliance_score": 92.0,
        "cibil_commercial_score": 760.0,
        "management_integrity_score": 8.0,
        "factory_capacity_utilization": 74.0,
        "due_diligence_risk_adjustment": 0.0,
        "collateral_coverage_ratio": 1.6,
        "collateral_type_score": 8.5,
    }
    decision = model.predict(features, requested_loan_amount=45.0, sector="agri_processing")
    assert 300 <= decision.credit_score <= 900
    assert decision.recommendation in {"APPROVE", "CONDITIONAL_APPROVE", "REJECT"}

