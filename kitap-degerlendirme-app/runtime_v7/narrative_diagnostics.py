from __future__ import annotations

from typing import Dict, List

from .contracts import EventGraph


def _count_connected_components(node_count: int, edges) -> (int, List[int]):
    if node_count == 0:
        return 0, []
    adj = {i: [] for i in range(node_count)}
    for e in edges or []:
        try:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)
        except Exception:
            continue

    seen = [False] * node_count
    components = []

    def dfs(start: int) -> int:
        stack = [start]
        size = 0
        seen[start] = True
        while stack:
            cur = stack.pop()
            size += 1
            for nb in adj.get(cur, []):
                if not seen[nb]:
                    seen[nb] = True
                    stack.append(nb)
        return size

    for i in range(node_count):
        if not seen[i]:
            components.append(dfs(i))

    return len(components), components


def compute_narrative_diagnostics(event_graph: EventGraph, narrative_graph: Dict, story_arc: Dict) -> Dict:
    nodes = event_graph.nodes or []
    edges = event_graph.edges or []

    event_count = len(nodes)
    generic_event_count = sum(1 for n in nodes if getattr(n, "generic_event", False))
    placeholder_event_count = sum(1 for n in nodes if getattr(n, "placeholder", False))

    def _is_meaningful(n) -> bool:
        # meaningful if not generic, not placeholder and has an action or outcome
        if getattr(n, "generic_event", False) or getattr(n, "placeholder", False):
            return False
        if getattr(n, "action", ""):
            return True
        if getattr(n, "outcome", ""):
            return True
        return False

    meaningful_event_count = sum(1 for n in nodes if _is_meaningful(n))

    total_nonzero = max(1, event_count)
    generic_ratio = generic_event_count / total_nonzero
    placeholder_ratio = placeholder_event_count / total_nonzero

    # disconnected components
    connected_component_count, components = _count_connected_components(event_count, edges)
    largest_component = max(components) if components else 0

    # main arc confidence: prefer event_graph diagnostics if present
    ev_diag = event_graph.diagnostics or {}
    ev_conf = ev_diag.get("confidence") if isinstance(ev_diag, dict) else {}
    main_arc_confidence = None
    if isinstance(ev_conf, dict) and ev_conf.get("score") is not None:
        try:
            main_arc_confidence = float(ev_conf.get("score"))
        except Exception:
            main_arc_confidence = None
    if main_arc_confidence is None:
        main_arc_confidence = max(0.0, 1.0 - (generic_ratio * 0.5 + placeholder_ratio * 0.5))

    # arc completeness: ratio of meaningful events weighted by confidence
    arc_completeness_score = (meaningful_event_count / total_nonzero) * main_arc_confidence

    # weak narrative reason rules
    weak_reason = "sufficient"
    if event_count == 0:
        weak_reason = "empty_event_graph"
    elif placeholder_ratio >= 0.6:
        weak_reason = "mostly_placeholder_events"
    elif generic_ratio >= 0.6:
        weak_reason = "mostly_generic_events"
    elif connected_component_count > 1 and event_count > 1:
        weak_reason = "disconnected_narrative"
    elif main_arc_confidence < 0.45:
        weak_reason = "low_arc_confidence"

    # disconnected events: nodes with no incoming and no outgoing edges
    connected_nodes = set()
    for e in edges:
        try:
            connected_nodes.add(e.source)
            connected_nodes.add(e.target)
        except Exception:
            continue
    disconnected_event_count = sum(1 for i in range(len(nodes)) if i not in connected_nodes)

    return {
        # legacy-preserved fields
        "story_arc_type": story_arc.get("type"),
        "generic_event_ratio": generic_ratio,
        "placeholder_event_ratio": placeholder_ratio,
        "disconnected_event_count": disconnected_event_count,
        "narrative_confidence": main_arc_confidence,
        # new fields
        "event_count": event_count,
        "meaningful_event_count": meaningful_event_count,
        "generic_event_count": generic_event_count,
        "placeholder_event_count": placeholder_event_count,
        "connected_component_count": connected_component_count,
        "main_arc_confidence": main_arc_confidence,
        "arc_completeness_score": arc_completeness_score,
        "weak_narrative_reason": weak_reason,
        "source": "runtime_v7_narrative_diagnostics",
    }
