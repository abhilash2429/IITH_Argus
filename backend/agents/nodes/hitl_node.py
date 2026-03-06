"""
Node 5: Human-in-the-Loop (HITL) Node
Pauses the LangGraph pipeline to wait for Credit Officer qualitative input.
The pipeline resumes when the Credit Officer submits notes via the API.
"""

import logging

from backend.agents.state import CreditAppraisalState

logger = logging.getLogger(__name__)


def hitl_node(state: CreditAppraisalState) -> CreditAppraisalState:
    """
    HITL pause point — sets current node and logs pause message.
    The graph is configured with interrupt_before=["hitl_node"],
    so execution will pause before this node runs.

    Args:
        state: Current pipeline state.

    Returns:
        State unchanged (waiting for Credit Officer input).
    """
    state["current_node"] = "hitl_node"
    state["log"].append(
        "[HITL] ⏸ Pipeline paused — waiting for Credit Officer qualitative input..."
    )
    state["log"].append(
        "[HITL] Please submit: qualitative notes, factory capacity %, "
        "and management assessment via the portal."
    )
    return state
