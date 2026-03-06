"""
LangGraph stateful graph definition — the MAIN ORCHESTRATOR of Intelli-Credit.

Graph Flow:
  document_router → ingestion_agent → gst_reconciler → research_agent
  → hitl_node (PAUSE for human input) → risk_scorer → cam_generator → END

Conditional edges:
  - After gst_reconciler: if circular_trading_detected, append fraud warning
  - hitl_node pauses and waits for Credit Officer to submit qualitative notes
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from backend.agents.state import CreditAppraisalState


def should_escalate_fraud(state: CreditAppraisalState) -> str:
    """Conditional edge: if circular trading detected, mark state before research."""
    if state.get("circular_trading_detected"):
        violations = state.get("rule_violations", [])
        violations.append("CRITICAL: Circular trading pattern detected in GST graph")
        state["rule_violations"] = violations
    return "research_agent"


def hitl_routing(state: CreditAppraisalState) -> str:
    """Route after HITL node: continue to scorer if complete, else loop back."""
    if state.get("hitl_complete"):
        return "risk_scorer"
    return "hitl_node"


def build_graph() -> StateGraph:
    """Build and compile the full credit appraisal LangGraph pipeline."""
    from backend.agents.nodes.document_router import document_router_node
    from backend.agents.nodes.ingestion_agent import ingestion_agent_node
    from backend.agents.nodes.gst_reconciler import gst_reconciler_node
    from backend.agents.nodes.research_agent import research_agent_node
    from backend.agents.nodes.hitl_node import hitl_node
    from backend.agents.nodes.risk_scorer import risk_scorer_node
    from backend.agents.nodes.cam_generator import cam_generator_node

    graph = StateGraph(CreditAppraisalState)

    # Add all 7 nodes
    graph.add_node("document_router", document_router_node)
    graph.add_node("ingestion_agent", ingestion_agent_node)
    graph.add_node("gst_reconciler", gst_reconciler_node)
    graph.add_node("research_agent", research_agent_node)
    graph.add_node("hitl_node", hitl_node)
    graph.add_node("risk_scorer", risk_scorer_node)
    graph.add_node("cam_generator", cam_generator_node)

    # Define edges
    graph.set_entry_point("document_router")
    graph.add_edge("document_router", "ingestion_agent")
    graph.add_edge("ingestion_agent", "gst_reconciler")
    graph.add_conditional_edges("gst_reconciler", should_escalate_fraud)
    graph.add_edge("research_agent", "hitl_node")
    graph.add_conditional_edges("hitl_node", hitl_routing)
    graph.add_edge("risk_scorer", "cam_generator")
    graph.add_edge("cam_generator", END)

    # Compile with memory checkpointer and HITL interrupt
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["hitl_node"])


# Global graph instance
credit_graph = build_graph()
