from __future__ import annotations

from typing import Dict, List

from .contracts import EventGraph


def build_narrative_graph(event_graph: EventGraph) -> Dict:
    nodes = event_graph.nodes or []
    edges = event_graph.edges or []

    # conflict links: nodes that declare conflict
    conflict_links = []
    for idx, node in enumerate(nodes):
        if getattr(node, "conflict", ""):
            conflict_links.append({"node": idx, "conflict": node.conflict})

    # resolution links: nodes that declare outcome/solution
    resolution_links = []
    for idx, node in enumerate(nodes):
        if getattr(node, "outcome", ""):
            resolution_links.append({"node": idx, "outcome": node.outcome})

    # dependency graph: actors co-occurrence
    dependency = {}
    for idx, node in enumerate(nodes):
        for actor in (node.actors or []):
            dependency.setdefault(actor, []).append(idx)

    # narrative transitions: derived from sequential edges
    transitions = []
    for e in edges:
        transitions.append({"from": e.source, "to": e.target, "relation": e.relation})

    diagnostics = {"source": "runtime_v7_narrative_graph_builder"}

    return {
        "nodes": [
            {"idx": i, "action": (n.action or ""), "actors": (n.actors or [])} for i, n in enumerate(nodes)
        ],
        "conflict_links": conflict_links,
        "resolution_links": resolution_links,
        "dependency": dependency,
        "transitions": transitions,
        "diagnostics": diagnostics,
    }
