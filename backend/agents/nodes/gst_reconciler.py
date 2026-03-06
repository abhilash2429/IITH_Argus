"""
Node 3: GST Reconciliation Agent
Cross-checks GST declared turnover with bank statement credits
and detects circular trading patterns in GST transaction graphs.
"""

import logging
from typing import Dict, List

from backend.agents.state import CreditAppraisalState
from backend.agents.tools.circular_trade import (
    check_gst_bank_mismatch,
    detect_circular_trading,
)

logger = logging.getLogger(__name__)


def gst_reconciler_node(state: CreditAppraisalState) -> CreditAppraisalState:
    """
    Reconcile GST filings with bank statements and check for circular trading.

    Args:
        state: Current pipeline state with extracted financials.

    Returns:
        Updated state with GST reconciliation results.
    """
    state["log"].append("[GST] Starting GST reconciliation...")

    financials = state.get("extracted_financials", {})
    gst_data = financials.get("gst", {})
    bank_data = financials.get("bank", {})
    gst_flags = []

    # GST vs Bank mismatch check
    gst_outward = gst_data.get("outward_supplies", 0) or 0
    bank_credits = bank_data.get("total_credits", 0) or 0

    mismatch_pct = check_gst_bank_mismatch(gst_outward, bank_credits)
    state["gst_bank_mismatch_pct"] = mismatch_pct

    if mismatch_pct > 25:
        gst_flags.append(
            f"CRITICAL: GST-Bank mismatch {mismatch_pct}% — possible revenue inflation"
        )
    elif mismatch_pct > 15:
        gst_flags.append(
            f"WARNING: GST-Bank mismatch {mismatch_pct}% — requires investigation"
        )

    # Circular trading detection
    transactions = gst_data.get("transactions", [])
    is_circular, entities = detect_circular_trading(transactions)
    state["circular_trading_detected"] = is_circular
    state["circular_trading_entities"] = entities

    if is_circular:
        gst_flags.append(
            f"CRITICAL: Circular trading detected involving: {', '.join(entities)}"
        )
        state["log"].append(
            f"[GST] ⚠️ CIRCULAR TRADING DETECTED — entities: {entities}"
        )

    # Bounced cheque check
    bounced = bank_data.get("bounced_cheques", 0)
    if bounced > 3:
        gst_flags.append(
            f"WARNING: {bounced} bounced cheques in 12 months — banking conduct issue"
        )

    state["gst_flags"] = gst_flags
    state["current_node"] = "gst_reconciler"
    state["log"].append(
        f"[GST] Reconciliation complete — mismatch: {mismatch_pct}%, "
        f"circular trading: {'YES' if is_circular else 'No'}, flags: {len(gst_flags)}"
    )
    return state
