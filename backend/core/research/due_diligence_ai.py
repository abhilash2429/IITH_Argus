"""
Due diligence note intelligence extraction.
"""

from __future__ import annotations

import re
from typing import List

from backend.config import settings
from backend.schemas.credit import DueDiligenceInsight


PROMPT_TEMPLATE = """
You are a senior credit analyst at an Indian bank. A field officer visited
{company_name} and wrote the following notes: "{free_text_notes}"

Extract: (1) List of risk factors mentioned, (2) List of positive factors,
(3) Suggested risk score adjustment (-50 to +20), (4) Key concerns to highlight
in the CAM. Format as JSON only.
""".strip()


class DueDiligenceAnalyzer:
    """
    LLM-enabled note parser with deterministic fallback.
    """

    risk_patterns = [
        r"idle machinery",
        r"overstated inventory",
        r"power outage",
        r"payment delay",
        r"evasiv",
        r"refused",
        r"non[-\s]?cooperative",
        r"low inventory",
        r"suspicious",
        r"contingent liabilit",
        r"worker unrest",
        r"compliance gap",
    ]
    positive_patterns = [
        r"new order",
        r"export growth",
        r"automation",
        r"cooperative",
        r"adequate inventory",
        r"healthy inventory",
        r"timely",
        r"healthy demand",
        r"expansion",
    ]

    async def analyze(self, company_name: str, free_text_notes: str) -> DueDiligenceInsight:
        if settings.llm_provider in {"openai", "anthropic"}:
            insight = await self._llm_analyze(company_name, free_text_notes)
            if insight:
                return insight
        return self._heuristic_analyze(free_text_notes)

    async def _llm_analyze(self, company_name: str, notes: str) -> DueDiligenceInsight | None:
        # LLM provider hookup intentionally guarded; system remains fully demoable without API keys.
        return None

    def _heuristic_analyze(self, notes: str) -> DueDiligenceInsight:
        low = notes.lower()
        risks = [p for p in self.risk_patterns if re.search(p, low)]
        positives = [p for p in self.positive_patterns if re.search(p, low)]

        negative_hits = len(risks)
        positive_hits = len(positives)
        score_adjustment = max(-50.0, min(20.0, positive_hits * 4.0 - negative_hits * 10.0))

        capacity_match = re.search(r"capacity_utilization_percent:\s*(\d+)", low)
        if capacity_match:
            cap = int(capacity_match.group(1))
            if cap < 45:
                score_adjustment -= 12
                risks.append("very_low_capacity")
            elif cap < 60:
                score_adjustment -= 6
                risks.append("suboptimal_capacity")
            elif cap >= 80:
                score_adjustment += 6
                positives.append("high_capacity_use")

        mgmt_rating_match = re.search(r"management_interview_rating:\s*(\d+)", low)
        if mgmt_rating_match:
            rating = int(mgmt_rating_match.group(1))
            if rating <= 2:
                score_adjustment -= 10
                risks.append("weak_management_assessment")
            elif rating >= 4:
                score_adjustment += 4
                positives.append("strong_management_assessment")

        if "inventory_levels: suspicious" in low:
            score_adjustment -= 10
            risks.append("suspicious_inventory")
        elif "inventory_levels: low" in low:
            score_adjustment -= 5
            risks.append("low_inventory")
        elif "inventory_levels: adequate" in low:
            score_adjustment += 2
            positives.append("adequate_inventory")

        if "management_cooperation: refused" in low:
            score_adjustment -= 12
            risks.append("management_refused_clarifications")
        elif "management_cooperation: evasive" in low:
            score_adjustment -= 8
            risks.append("management_evasive")
        elif "management_cooperation: cooperative" in low:
            score_adjustment += 3
            positives.append("management_cooperative")

        score_adjustment = max(-50.0, min(20.0, score_adjustment))

        sentiment = "NEUTRAL"
        if score_adjustment <= -10:
            sentiment = "NEGATIVE"
        elif score_adjustment >= 8:
            sentiment = "POSITIVE"

        cam_concerns: List[str] = []
        if risks:
            cam_concerns.append("Field visit identified operational risk signals.")
        if "inventory" in low:
            cam_concerns.append("Inventory quality and valuation to be validated quarterly.")
        if "capacity" in low and "40" in low:
            cam_concerns.append("Low observed capacity utilization may pressure debt servicing.")

        return DueDiligenceInsight(
            sentiment=sentiment,
            risk_factors=[r.replace("\\", "") for r in risks],
            positive_factors=[p.replace("\\", "") for p in positives],
            score_adjustment=score_adjustment,
            cam_concerns=cam_concerns,
        )
