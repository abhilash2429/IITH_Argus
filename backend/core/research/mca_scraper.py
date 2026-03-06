"""
MCA lookup provider with mock fallback.
"""

from __future__ import annotations

from datetime import date
from typing import List

from backend.schemas.credit import Charge, Director, MCAReport


class MCAScraper:
    """
    MCA scraper abstraction.
    Live portal automation is brittle; we keep a stable mock provider for demos.
    """

    async def lookup(self, company_name: str, cin: str | None = None) -> MCAReport:
        # For hackathon reliability, return deterministic mock data that mirrors MCA structure.
        normalized = company_name.strip() or "Unknown Company"
        cin_value = cin or "U01110TG2012PTC081245"
        directors: List[Director] = [
            Director(name="Ravi Kumar", din="08219033", status="ACTIVE"),
            Director(name="Anita Sharma", din="07900211", status="ACTIVE"),
        ]

        struck_off = []
        red_flags = []
        if "traders" in normalized.lower():
            struck_off = ["SKM Agro Exim Pvt Ltd (Struck Off - 2021)"]
            red_flags.append("Director linked with struck-off company.")

        charges = [
            Charge(lender="State Bank of India", amount=18_50_00_000, charge_type="Hypothecation"),
            Charge(lender="HDFC Bank", amount=6_75_00_000, charge_type="Mortgage"),
        ]

        return MCAReport(
            company_cin=cin_value,
            registration_date=date(2012, 5, 14),
            authorized_capital=25_00_00_000,
            paid_up_capital=14_20_00_000,
            directors=directors,
            associated_struck_off_companies=struck_off,
            registered_charges=charges,
            filing_compliance_score=92.0 if not struck_off else 78.0,
            last_agm_date=date(2025, 9, 28),
            mca_red_flags=red_flags,
        )

