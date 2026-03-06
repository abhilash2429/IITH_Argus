"""
eCourts litigation checker with deterministic mock fallback.
"""

from __future__ import annotations

from datetime import date
from typing import List

from backend.schemas.credit import FindingType, ResearchFinding, Severity


class ECourtsScraper:
    async def search(self, company_name: str) -> List[ResearchFinding]:
        findings: List[ResearchFinding] = []
        low = company_name.lower()

        if "agri" in low:
            findings.append(
                ResearchFinding(
                    source_url="https://ecourts.example/case/2024-cs-102",
                    source_name="eCourts (Mock)",
                    finding_type=FindingType.LITIGATION,
                    summary="One commercial recovery suit filed by a packaging vendor; matter under mediation.",
                    severity=Severity.MEDIUM,
                    date_of_finding=date(2024, 11, 4),
                    confidence=0.74,
                    raw_snippet="Civil Suit 102/2024 - vendor payment dispute, amount disputed ₹42 lakh.",
                )
            )
        else:
            findings.append(
                ResearchFinding(
                    source_url="https://ecourts.example/no-major-cases",
                    source_name="eCourts (Mock)",
                    finding_type=FindingType.NEUTRAL,
                    summary="No material litigation found in district and high court records.",
                    severity=Severity.INFORMATIONAL,
                    date_of_finding=date(2025, 8, 1),
                    confidence=0.68,
                    raw_snippet="No significant cases were linked to this entity in sampled jurisdictions.",
                )
            )
        return findings

