from backend.core.ingestion.gst_parser import GSTMismatchAnalyzer, GSTParser


def test_gst_mismatch_analyzer_high_risk():
    parser = GSTParser()
    g3 = parser.parse_payload(
        {
            "return_type": "GSTR3B",
            "period": "2025-10",
            "outward_supplies": 12000000,
            "itc_claimed": 2400000,
            "tax_paid": 2100000,
        }
    ).gstr3b
    g2 = parser.parse_payload(
        {
            "return_type": "GSTR2A",
            "period": "2025-10",
            "available_itc": 1500000,
            "vendor_purchases": {"V1": 700000, "V2": 800000},
        }
    ).gstr2a

    report = GSTMismatchAnalyzer().analyze(g3, g2, bank_credits=7000000)
    assert report.itc_inflation_percentage > 20
    assert report.risk_level.value in {"HIGH", "CRITICAL"}

