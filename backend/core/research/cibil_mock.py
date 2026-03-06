"""
Mock CIBIL commercial score provider for offline demos.
"""

from __future__ import annotations

import hashlib


def get_mock_cibil_score(company_name: str) -> float:
    """
    Deterministically map company name to a pseudo CIBIL score (550-860).
    """
    digest = hashlib.sha256(company_name.lower().encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)
    return float(550 + (seed % 311))

