"""
Circular Trading Detector using NetworkX graph analysis.
Detects fraudulent circular GST transaction patterns where
companies inflate revenue through round-tripping invoices.

Also checks GST vs bank statement mismatch for revenue inflation signals.
"""

import logging
from typing import List, Tuple

import networkx as nx

logger = logging.getLogger(__name__)


def build_gst_graph(transactions: List[dict]) -> nx.DiGraph:
    """
    Build a directed graph from GST transactions.

    Args:
        transactions: List of dicts with seller_gstin, buyer_gstin, value.

    Returns:
        NetworkX DiGraph with weighted edges.
    """
    G = nx.DiGraph()
    for txn in transactions:
        G.add_edge(
            txn["seller_gstin"],
            txn["buyer_gstin"],
            weight=txn.get("value", 0),
        )
    return G


def detect_circular_trading(transactions: List[dict]) -> Tuple[bool, List[str]]:
    """
    Detect circular trading patterns in GST transaction graph.

    Args:
        transactions: List of transaction dicts.

    Returns:
        Tuple of (is_circular: bool, list_of_circular_entities: List[str]).
    """
    if not transactions:
        return False, []

    G = build_gst_graph(transactions)

    try:
        cycle = nx.find_cycle(G, orientation="original")
        # Extract unique entities involved in the cycle
        entities = list(set([edge[0] for edge in cycle] + [edge[1] for edge in cycle]))
        logger.warning(f"[CircularTrade] Cycle detected involving: {entities}")
        return True, entities
    except nx.NetworkXNoCycle:
        return False, []


def check_gst_bank_mismatch(
    gst_outward_supplies: float, bank_total_credits: float
) -> float:
    """
    Compare GST-declared turnover with actual bank credits.

    Red flags:
    - Mismatch > 25%: Potential revenue inflation
    - GST > Bank: Possible fictitious invoicing
    - Bank >> GST: Possible GST evasion

    Args:
        gst_outward_supplies: Total outward supplies from GSTR-3B.
        bank_total_credits: Total credits from bank statement.

    Returns:
        Mismatch percentage (0-100).
    """
    if not gst_outward_supplies or not bank_total_credits:
        return 0.0

    mismatch = abs(gst_outward_supplies - bank_total_credits) / max(
        gst_outward_supplies, bank_total_credits
    )
    return round(mismatch * 100, 2)
