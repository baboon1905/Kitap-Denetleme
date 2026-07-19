from __future__ import annotations

from typing import Dict, List

from .contracts import EventGraph


def enrich_event_graph(event_graph: EventGraph) -> EventGraph:
    nodes = event_graph.nodes or []
    edges = event_graph.edges or []

    # actor references: map actor name -> list of node indices
    actor_refs: Dict[str, List[int]] = {}
    for idx, node in enumerate(nodes):
        for actor in (node.actors or []):
            actor_refs.setdefault(actor, []).append(idx)

    # temporal order: use sequential edges if present otherwise node order
    temporal_order: List[int] = []
    if edges:
        seq = [e for e in edges if getattr(e, "relation", "") == "sequential"]
        if seq and len(seq) + 1 == len(nodes):
            temporal_order = list(range(len(nodes)))
    if not temporal_order:
        temporal_order = list(range(len(nodes)))

    # causal links: placeholder empty list (can be extended later)
    causal_links: List[Dict] = []

    # confidence: heuristic from node flags
    total = max(1, len(nodes))
    generic_count = sum(1 for n in nodes if getattr(n, "generic_event", False))
    placeholder_count = sum(1 for n in nodes if getattr(n, "placeholder", False))
    generic_ratio = generic_count / total
    placeholder_ratio = placeholder_count / total
    confidence_score = max(0.0, 1.0 - (generic_ratio * 0.5 + placeholder_ratio * 0.5))

    diagnostics = {
        "actor_references": actor_refs,
        "temporal_order": temporal_order,
        "causal_links": causal_links,
        "confidence": {
            "score": confidence_score,
            "generic_ratio": generic_ratio,
            "placeholder_ratio": placeholder_ratio,
        },
        "source": "runtime_v7_event_graph_enricher",
    }

    return EventGraph(nodes=nodes, edges=edges, diagnostics=diagnostics)
