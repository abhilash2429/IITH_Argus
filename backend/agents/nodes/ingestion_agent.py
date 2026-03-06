"""
Node 2: Ingestion Agent
Extracts structured data from each classified document using a 3-tier strategy:
  Tier 1: pdfplumber (fast, accurate for digital PDFs)
  Tier 2: Qwen2.5-VL OCR (scanned/Indic PDFs)
  Tier 3: Tesseract OCR (open source fallback)

After extraction, calls type-specific parsers and embeds chunks to Qdrant.
"""

import logging
import re
from typing import Dict, List, Tuple

import pdfplumber

from backend.agents.state import CreditAppraisalState
from backend.agents.llm.llm_client import llm_call_json

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 100


def extract_text_pdfplumber(pdf_path: str) -> str:
    """
    Extract text from digital PDF using pdfplumber.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text string.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_tesseract(pdf_path: str) -> str:
    """
    Fallback OCR using Tesseract (supports Indian language packs).

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text string.
    """
    from pdf2image import convert_from_path
    import pytesseract

    images = convert_from_path(pdf_path, dpi=200)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang="eng+hin") + "\n"
    return text.strip()


def smart_extract(pdf_path: str) -> Tuple[str, str]:
    """
    Smart extraction with 3-tier fallback: pdfplumber → Qwen2.5-VL → Tesseract.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Tuple of (extracted_text, method_used).
    """
    # Tier 1: pdfplumber
    text = extract_text_pdfplumber(pdf_path)
    if len(text) >= MIN_TEXT_LENGTH:
        return text, "pdfplumber"

    # Tier 2: Qwen2.5-VL OCR
    try:
        from backend.core.ingestion.qwen_vl_ocr import QwenVLOCR

        ocr = QwenVLOCR()
        result = ocr.extract_text_from_pdf(pdf_path)
        text = result.text
        if len(text) >= MIN_TEXT_LENGTH:
            return text, result.method
    except Exception as e:
        logger.warning(f"[Ingestion] Qwen2.5-VL extraction failed: {e}")

    # Tier 3: Tesseract fallback
    try:
        text = extract_text_tesseract(pdf_path)
    except Exception as e:
        logger.warning(f"[Ingestion] Tesseract failed: {e}")
        text = ""

    return text, "tesseract"


def parse_gst_filing(text: str) -> Dict:
    """
    Extract key GST metrics from GSTR-3B/GSTR-1 text using regex.

    Args:
        text: Raw extracted text from GST filing.

    Returns:
        Dict with gstin, outward_supplies, itc_claimed, filing_period.
    """
    data = {}

    # GSTIN pattern: 15-digit alphanumeric
    gstin_match = re.search(
        r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text
    )
    data["gstin"] = gstin_match.group() if gstin_match else None

    # Outward supplies total
    outward_match = re.search(
        r"outward taxable supplies[^\d]*([\d,]+\.?\d*)", text, re.IGNORECASE
    )
    data["outward_supplies"] = (
        float(outward_match.group(1).replace(",", "")) if outward_match else None
    )

    # ITC claimed
    itc_match = re.search(
        r"input tax credit[^\d]*([\d,]+\.?\d*)", text, re.IGNORECASE
    )
    data["itc_claimed"] = (
        float(itc_match.group(1).replace(",", "")) if itc_match else None
    )

    # Filing period
    period_match = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})",
        text,
        re.IGNORECASE,
    )
    data["filing_period"] = period_match.group() if period_match else None

    return data


def parse_bank_statement(text: str) -> Dict:
    """
    Extract aggregated bank data from statement text using regex.

    Args:
        text: Raw extracted text from bank statement.

    Returns:
        Dict with total_credits, total_debits, bounced_cheques, emi_debits.
    """
    data = {
        "total_credits": 0,
        "total_debits": 0,
        "bounced_cheques": 0,
        "emi_debits": 0,
        "large_cash_deposits": 0,
        "transactions": [],
    }

    data["bounced_cheques"] = len(
        re.findall(r"(chq.{0,10}return|bounce|dishonour)", text, re.IGNORECASE)
    )
    data["emi_debits"] = len(re.findall(r"(emi|ecs|nach)", text, re.IGNORECASE))

    credit_matches = re.findall(r"cr[^\d]*([\d,]+\.?\d*)", text, re.IGNORECASE)
    debit_matches = re.findall(r"dr[^\d]*([\d,]+\.?\d*)", text, re.IGNORECASE)

    data["total_credits"] = sum(
        float(m.replace(",", "")) for m in credit_matches[:100]
    )
    data["total_debits"] = sum(
        float(m.replace(",", "")) for m in debit_matches[:100]
    )

    return data


def parse_annual_report(text: str) -> Dict:
    """
    Use LLM to extract structured financial data from annual report.
    Annual reports are too complex for regex — uses llm_call_json().

    Args:
        text: Raw extracted text from annual report.

    Returns:
        Dict with financial metrics.
    """
    prompt = f"""
    You are a financial analyst. Extract the following from this annual report text.
    Return ONLY valid JSON with these exact keys:

    {{
        "revenue_crore": [year1_value, year2_value, year3_value],
        "ebitda_crore": float,
        "ebitda_margin_pct": float,
        "pat_crore": float,
        "total_debt_crore": float,
        "net_worth_crore": float,
        "current_ratio": float,
        "dscr": float,
        "promoter_holding_pct": float,
        "auditor_opinion": "qualified" | "unqualified" | "adverse" | "disclaimer",
        "key_risks": ["risk1", "risk2"],
        "directors": ["name1", "name2"],
        "company_name": "string",
        "cin": "string",
        "current_assets_crore": float,
        "current_liabilities_crore": float,
        "sector": "string"
    }}

    If a value cannot be found, use null.

    ANNUAL REPORT TEXT:
    {text[:8000]}
    """

    return llm_call_json(prompt, task="annual_report_extraction", max_tokens=2000)


def ingestion_agent_node(state: CreditAppraisalState) -> CreditAppraisalState:
    """
    Main ingestion node — processes all classified documents.
    Extracts text, runs type-specific parsers, embeds to Qdrant.

    Args:
        state: Current pipeline state.

    Returns:
        Updated state with extracted data and financials.
    """
    state["log"].append("[Ingestion] Starting document extraction...")

    for doc in state["documents"]:
        try:
            # Smart extraction with 3-tier fallback
            raw_text, method = smart_extract(doc["path"])
            doc["raw_text"] = raw_text
            doc["extraction_method"] = method

            # Type-specific parsing
            if doc["type"] == "GST_FILING":
                doc["extracted_data"] = parse_gst_filing(raw_text)
            elif doc["type"] == "BANK_STATEMENT":
                doc["extracted_data"] = parse_bank_statement(raw_text)
            elif doc["type"] == "ANNUAL_REPORT":
                doc["extracted_data"] = parse_annual_report(raw_text)
            elif doc["type"] == "LEGAL_NOTICE":
                doc["extracted_data"] = {"text": raw_text[:2000], "type": "legal"}
            elif doc["type"] == "ITR":
                doc["extracted_data"] = {"text": raw_text[:2000], "type": "itr"}
            elif doc["type"] == "SANCTION_LETTER":
                doc["extracted_data"] = {"text": raw_text[:2000], "type": "sanction"}
            elif doc["type"] == "RATING_REPORT":
                doc["extracted_data"] = {"text": raw_text[:2000], "type": "rating"}

            state["log"].append(
                f"[Ingestion] {doc['type']} extracted via {method} — {len(raw_text)} chars"
            )

            # Embed chunks into Qdrant
            try:
                _embed_document_to_qdrant(doc, state["company_id"])
            except Exception as e:
                logger.warning(f"[Ingestion] Qdrant embedding failed: {e}")
                state["errors"].append(f"[Ingestion] Qdrant embed failed: {e}")

        except Exception as e:
            logger.error(f"[Ingestion] Failed to process {doc['path']}: {e}")
            state["errors"].append(f"[Ingestion] Extraction failed for {doc['path']}: {e}")

    # Consolidate all extracted financials
    state["extracted_financials"] = _consolidate_financials(state["documents"])
    state["current_node"] = "ingestion_agent"
    state["log"].append("[Ingestion] Document extraction complete")
    return state


def _embed_document_to_qdrant(doc: Dict, company_id: str) -> None:
    """
    Chunk document text and upsert to Qdrant for RAG queries.

    Args:
        doc: Document dict with raw_text and type.
        company_id: Company identifier for filtering.
    """
    from backend.vector_store.qdrant_client import upsert_document_chunks
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-m3")

    text = doc.get("raw_text") or ""
    if not text:
        return

    # 500-char overlapping windows with stride 400
    chunks = [text[i : i + 500] for i in range(0, len(text), 400)]
    if not chunks:
        return

    embeddings = model.encode(chunks).tolist()

    payloads = [
        {
            "company_id": company_id,
            "doc_type": doc["type"],
            "chunk_text": chunk,
            "chunk_index": i,
        }
        for i, chunk in enumerate(chunks)
    ]

    upsert_document_chunks(embeddings, payloads)


def _consolidate_financials(documents: List[Dict]) -> Dict:
    """
    Merge extracted data from all documents into a single financials dict.

    Args:
        documents: List of classified and extracted document dicts.

    Returns:
        Consolidated financials dict.
    """
    financials = {}
    for doc in documents:
        if doc["type"] == "ANNUAL_REPORT":
            financials.update(doc.get("extracted_data", {}))
        elif doc["type"] == "GST_FILING":
            financials["gst"] = doc.get("extracted_data", {})
        elif doc["type"] == "BANK_STATEMENT":
            financials["bank"] = doc.get("extracted_data", {})
    return financials
