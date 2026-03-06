"""
News and promoter intelligence provider.
"""

from __future__ import annotations

from datetime import date
from typing import List

from backend.config import settings
from backend.schemas.credit import FindingType, ResearchFinding, Severity


class NewsScraper:
    """
    Mock-first provider with optional live extensions.
    """

    async def search_company(self, company_name: str, sector: str) -> List[ResearchFinding]:
        findings: List[ResearchFinding] = [
            ResearchFinding(
                source_url="https://news.example/sector-outlook-agri-processing-2026",
                source_name="Sector Pulse (Mock)",
                finding_type=FindingType.SECTOR,
                summary=(
                    f"{sector.replace('_', ' ').title()} sector expected to remain stable with moderate "
                    "margin pressure due to logistics costs."
                ),
                severity=Severity.LOW,
                date_of_finding=date(2026, 1, 10),
                confidence=0.72,
                raw_snippet="Sector growth 8-10%, but working capital cycles remain stretched.",
            )
        ]

        if "vardhman" in company_name.lower():
            findings.append(
                ResearchFinding(
                    source_url="https://news.example/vardhman-promoter-tax-query",
                    source_name="Business Chronicle (Mock)",
                    finding_type=FindingType.FRAUD_ALERT,
                    summary=(
                        "One promoter entity was issued an income-tax query notice; no prosecution reported."
                    ),
                    severity=Severity.MEDIUM,
                    date_of_finding=date(2025, 7, 22),
                    confidence=0.66,
                    raw_snippet="Tax department sought clarification on inter-company transactions.",
                )
            )
        return findings

    async def search_promoter(self, promoter_name: str) -> List[ResearchFinding]:
        low = promoter_name.lower()
        if "kumar" in low:
            return [
                ResearchFinding(
                    source_url="https://news.example/promoter-award",
                    source_name="Economic Times (Mock)",
                    finding_type=FindingType.NEUTRAL,
                    summary="Promoter received an MSME export award in 2024.",
                    severity=Severity.INFORMATIONAL,
                    date_of_finding=date(2024, 9, 2),
                    confidence=0.61,
                    raw_snippet="Awarded by state exports promotion council.",
                )
            ]
        return []

