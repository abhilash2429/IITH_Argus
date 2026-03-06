"""
Generate realistic sample data for Vardhman Agri Processing Pvt. Ltd.
"""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path
from random import Random

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_gstr3b(path: Path) -> None:
    rng = Random(42)
    months = []
    year = 2025
    for month in range(1, 13):
        outward = 6.2 + rng.uniform(-0.5, 0.8)
        itc = 0.95 + rng.uniform(-0.08, 0.12)
        available_itc = itc - rng.uniform(0.0, 0.04)
        if month == 10:
            # suspicious month: inflated ITC
            itc += 0.24
        months.append(
            {
                "return_type": "GSTR3B",
                "period": f"{year}-{month:02d}",
                "outward_supplies": round(outward * 1_00_00_000, 2),
                "itc_claimed": round(itc * 1_00_00_000, 2),
                "available_itc": round(available_itc * 1_00_00_000, 2),
                "tax_paid": round((outward * 0.18) * 1_00_00_000, 2),
            }
        )
    path.write_text(json.dumps(months, indent=2), encoding="utf-8")


def generate_bank_statement(path: Path) -> None:
    rng = Random(7)
    start = date(2025, 4, 1)
    rows = []
    balance = 2_40_00_000.0
    for day in range(365):
        d = start + timedelta(days=day)
        if d.day in {5, 12, 19, 26}:
            credit = rng.uniform(8_00_000, 24_00_000)
            debit = rng.uniform(5_00_000, 18_00_000)
            party = "Distributor Collection"
            narration = "NEFT Customer Receipts"
            if d.month == 3 and d.day > 18:
                # window dressing spike
                credit *= 3.4
                narration = "Inter-Corporate Deposit Inward"
                party = "VAP Group Holding"
            balance += credit - debit
            rows.append(
                {
                    "date": d.isoformat(),
                    "debit": round(debit, 2),
                    "credit": round(credit, 2),
                    "balance": round(balance, 2),
                    "narration": narration,
                    "party": party,
                }
            )

        if d.day in {10, 20}:
            emi = 6_45_000
            balance -= emi
            rows.append(
                {
                    "date": d.isoformat(),
                    "debit": emi,
                    "credit": 0.0,
                    "balance": round(balance, 2),
                    "narration": "NACH EMI TERM LOAN",
                    "party": "State Bank of India",
                }
            )

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["date", "debit", "credit", "balance", "narration", "party"]
        )
        writer.writeheader()
        writer.writerows(rows)


def generate_itr(path: Path) -> None:
    payload = {
        "assessment_year": "2025-26",
        "pan": "AAACV1234L",
        "gross_revenue": 71_80_00_000,
        "taxable_income": 5_40_00_000,
        "tax_paid": 1_38_00_000,
        "depreciation": 1_22_00_000,
        "note": "Revenue intentionally 7-8% lower than aggregate GST turnover for demo inconsistency.",
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def generate_research(path: Path) -> None:
    findings = [
        {
            "source_url": "https://business-standard.example/vardhman-agri-capacity-expansion",
            "source_name": "Business Standard (Mock)",
            "finding_type": "SECTOR",
            "summary": "Company announced a capacity expansion with partial debt funding.",
            "severity": "LOW",
            "date_of_finding": "2025-09-11",
            "confidence": 0.76,
            "raw_snippet": "Board approved Rs 48 crore capex to add solvent extraction line.",
        },
        {
            "source_url": "https://times-now.example/promoter-tax-query-vardhman",
            "source_name": "Times Now Biz (Mock)",
            "finding_type": "FRAUD_ALERT",
            "summary": "Promoter received income-tax query on related-party transactions.",
            "severity": "MEDIUM",
            "date_of_finding": "2025-07-22",
            "confidence": 0.66,
            "raw_snippet": "Department issued notice seeking reconciliations; no prosecution initiated.",
        },
    ]
    path.write_text(json.dumps(findings, indent=2), encoding="utf-8")


def generate_annual_report(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    for page in range(1, 41):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, "Vardhman Agri Processing Pvt. Ltd. - Annual Report 2025")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 80, f"Page {page}")

        y = height - 120
        lines = [
            "Directors' Report: The Company delivered steady growth in FY25.",
            "Standalone Financial Statements prepared under Ind AS.",
            "Revenue from Operations: INR 78.2 crore (FY25), 72.4 crore (FY24), 66.9 crore (FY23).",
            "Profit After Tax: INR 4.8 crore (FY25).",
            "Total Debt: INR 24.5 crore. Current Ratio: 1.38. DSCR: 1.52.",
            "Related Party Transactions were conducted at arm's length.",
            "Auditors' comments: emphasis of matter on delayed debtor recoveries.",
            "No going concern uncertainty has been identified by management.",
        ]
        for line in lines:
            c.drawString(50, y, line)
            y -= 22

        c.showPage()
    c.save()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / "sample_documents"
    out.mkdir(parents=True, exist_ok=True)

    generate_gstr3b(out / "sample_gstr3b.json")
    generate_bank_statement(out / "sample_bank_statement.csv")
    generate_itr(out / "sample_itr.json")
    generate_research(out / "sample_research_findings.json")
    generate_annual_report(out / "sample_annual_report.pdf")
    print(f"Sample data generated at: {out}")


if __name__ == "__main__":
    main()

