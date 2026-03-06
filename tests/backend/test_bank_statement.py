from pathlib import Path

import pandas as pd

from backend.core.ingestion.bank_statement import BankStatementAnalyzer


def test_bank_statement_window_dressing(tmp_path: Path):
    rows = [
        {"date": "2025-03-02", "debit": 100000, "credit": 200000, "balance": 500000, "narration": "NEFT", "party": "Customer A"},
        {"date": "2025-03-10", "debit": 120000, "credit": 250000, "balance": 630000, "narration": "NEFT", "party": "Customer B"},
        {"date": "2025-03-20", "debit": 50000, "credit": 1500000, "balance": 2080000, "narration": "Inter-Corporate Deposit", "party": "Group Entity"},
        {"date": "2025-03-27", "debit": 60000, "credit": 1800000, "balance": 3820000, "narration": "Inter-Corporate Deposit", "party": "Group Entity"},
    ]
    csv_path = tmp_path / "bank.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    metrics = BankStatementAnalyzer().analyze(str(csv_path), annual_revenue=2_00_00_000, gst_turnover=2_20_00_000)
    assert metrics.year_end_window_dressing is True
    assert metrics.banking_turnover > 0

