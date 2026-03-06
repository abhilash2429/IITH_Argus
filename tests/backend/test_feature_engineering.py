from backend.core.ml.feature_engineering import build_feature_vector


def test_feature_vector_shape():
    vector = build_feature_vector(
        {
            "financials": {"dscr": 1.5, "debt_equity_ratio": 1.4},
            "bank_metrics": {"banking_to_gst_ratio": 0.98, "abb_to_claimed_revenue_ratio": 0.12},
            "gst": {"itc_inflation_percentage": 4.0, "revenue_inflation_flag": False},
            "cross_validation": {"itr_vs_gst_revenue_gap": 6.0, "debt_service_coverage_ratio": 1.4},
            "research": {"mca_filing_compliance_score": 91.0, "cibil_commercial_score": 734},
            "due_diligence": {"management_integrity_score": 7.5, "factory_capacity_utilization": 72},
            "collateral": {"collateral_coverage_ratio": 1.4, "collateral_type_score": 8.0},
            "sector": "agri_processing",
        }
    )
    assert "dscr" in vector
    assert "cibil_commercial_score" in vector
    assert len(vector) >= 20

