"""
Shared state schema for the LangGraph credit appraisal pipeline.
Every node reads from and writes to this TypedDict.
This is the single source of truth for pipeline data flow.
"""

from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum


class RiskCategory(str, Enum):
    """Risk classification categories for credit decisions."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CreditAppraisalState(TypedDict):
    """
    Complete state that flows through the LangGraph pipeline.
    All nodes read from and write to this structure.
    """

    # ── Identity ─────────────────────────────────────────────────────
    company_id: str
    company_name: str

    # ── Document tracking ────────────────────────────────────────────
    uploaded_document_paths: List[str]
    documents: List[Dict]  # [{path, type, raw_text, extracted_data, extraction_method}]

    # ── Extracted financial data (consolidated from all docs) ────────
    extracted_financials: Dict[str, Any]

    # ── GST reconciliation ───────────────────────────────────────────
    gst_bank_mismatch_pct: Optional[float]
    circular_trading_detected: bool
    circular_trading_entities: List[str]
    gst_flags: List[str]

    # ── Research results ─────────────────────────────────────────────
    news_summary: str
    mca_data: Dict[str, Any]
    litigation_data: List[Dict]
    rbi_regulatory_flags: List[str]
    promoter_background: Dict[str, Any]
    research_red_flags: List[str]

    # ── Severity pre-classifier output ───────────────────────────────
    severity_summary: Dict[str, Any]

    # ── Human-in-the-loop (qualitative inputs from Credit Officer) ───
    qualitative_notes: Optional[str]
    site_visit_capacity_pct: Optional[float]
    management_assessment: Optional[str]
    hitl_complete: bool

    # ── Risk scoring ─────────────────────────────────────────────────
    rule_based_score: Optional[float]       # 0-100 (100 = lowest risk)
    ml_stress_probability: Optional[float]  # 0-1 (1 = highest stress)
    final_risk_score: Optional[float]       # blended 0-100
    risk_category: Optional[str]
    shap_values: Optional[Dict[str, float]]  # feature_name -> contribution
    rule_violations: List[str]               # list of triggered rules
    risk_strengths: List[str]                # positive factors
    critical_hit: bool

    # ── Decision ─────────────────────────────────────────────────────
    decision: Optional[str]                  # APPROVE | CONDITIONAL_APPROVE | REJECT
    recommended_loan_limit_crore: Optional[float]
    interest_rate_premium_bps: Optional[int]  # basis points over base rate
    decision_rationale: str

    # ── CAM output ───────────────────────────────────────────────────
    cam_text: Optional[str]
    cam_docx_path: Optional[str]
    cam_pdf_path: Optional[str]

    # ── Pipeline metadata ────────────────────────────────────────────
    current_node: str
    log: List[str]
    errors: List[str]
