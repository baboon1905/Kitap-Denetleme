from __future__ import annotations

from typing import Dict, List

from .contracts import EventGraph


def plan_story_arc(event_graph: EventGraph) -> Dict:
    nodes = event_graph.nodes or []
    n = len(nodes)

    def node_action(idx: int) -> str:
        if idx < 0 or idx >= n:
            return ""
        node = nodes[idx]
        parts = []
        if getattr(node, "action", ""):
            parts.append(node.action)
        if getattr(node, "conflict", ""):
            parts.append(node.conflict)
        if getattr(node, "outcome", ""):
            parts.append(node.outcome)
        return " - ".join(parts)

    if n == 0:
        stages = {}
    else:
        intro = node_action(0)
        inciting = node_action(1) if n > 1 else ""
        climax_idx = n // 2
        rising = " ".join([node_action(i) for i in range(2, max(2, climax_idx))]) if n > 3 else ""
        climax = node_action(climax_idx)
        resolution = node_action(n - 2) if n > 2 else ""
        ending = node_action(n - 1)
        stages = {
            "introduction": intro,
            "inciting_incident": inciting,
            "rising_action": rising,
            "climax": climax,
            "resolution": resolution,
            "ending": ending,
        }

    arc_type = "linear" if n <= 6 else "complex"

    return {
        "type": arc_type,
        "stages": stages,
        "source": "runtime_v7_story_arc_planner",
    }
