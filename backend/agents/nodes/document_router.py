"""
Node 1: Document Router
Classifies uploaded PDFs into document types so downstream agents
know which extraction strategy to apply.

Document Types:
  ANNUAL_REPORT, GST_FILING, BANK_STATEMENT, ITR,
  LEGAL_NOTICE, SANCTION_LETTER, RATING_REPORT, UNKNOWN
"""

import logging
from typing import Dict, List

import pdfplumber

from backend.agents.state import CreditAppraisalState

logger = logging.getLogger(__name__)

DOCUMENT_KEYWORDS: Dict[str, List[str]] = {
    "ANNUAL_REPORT": [
        "director's report", "auditor's report", "balance sheet",
        "statement of profit", "annual report",
    ],
    "GST_FILING": [
        "gstr", "gstin", "outward supplies", "inward supplies",
        "input tax credit", "igst", "cgst", "sgst",
    ],
    "BANK_STATEMENT": [
        "account number", "account no", "transaction date",
        "debit", "credit", "balance", "ifsc",
    ],
    "ITR": [
        "income tax return", "assessment year", "pan",
        "gross total income", "tax payable",
    ],
    "LEGAL_NOTICE": [
        "hon'ble court", "plaintiff", "defendant", "petition",
        "writ", "recovery suit", "drt",
    ],
    "SANCTION_LETTER": [
        "sanction letter", "sanctioned limit", "rate of interest",
        "repayment schedule", "drawing power",
    ],
    "RATING_REPORT": [
        "crisil", "icra", "care ratings", "brickwork",
        "credit rating", "rating rationale",
    ],
}


def classify_document(text: str) -> str:
    """
    Classify a document based on keyword scoring.

    Args:
        text: Extracted text from first 2 pages of the document.

    Returns:
        Document type string (e.g., "ANNUAL_REPORT", "UNKNOWN").
    """
    text_lower = text.lower()
    scores = {}
    for doc_type, keywords in DOCUMENT_KEYWORDS.items():
        scores[doc_type] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "UNKNOWN"


def document_router_node(state: CreditAppraisalState) -> CreditAppraisalState:
    """
    Reads each uploaded PDF, extracts first 2 pages of text,
    classifies document type, and updates state.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with classified documents.
    """
    state["log"].append("[Router] Starting document classification...")
    classified_docs = []

    for doc_path in state["uploaded_document_paths"]:
        try:
            with pdfplumber.open(doc_path) as pdf:
                sample_text = ""
                for page in pdf.pages[:2]:
                    sample_text += (page.extract_text() or "")
            doc_type = classify_document(sample_text)
        except Exception as e:
            logger.warning(f"[Router] Failed to classify {doc_path}: {e}")
            doc_type = "UNKNOWN"
            state["errors"].append(f"[Router] Classification failed for {doc_path}: {e}")

        classified_docs.append({
            "path": doc_path,
            "type": doc_type,
            "raw_text": None,
            "extracted_data": {},
            "extraction_method": None,
        })

    state["documents"] = classified_docs
    state["current_node"] = "document_router"
    state["log"].append(
        f"[Router] Classified {len(classified_docs)} documents: "
        + ", ".join(d["type"] for d in classified_docs)
    )
    return state
