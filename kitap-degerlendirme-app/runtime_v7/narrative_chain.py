from __future__ import annotations

from typing import Any, Dict, List

from .contracts import EventGraph


def _event_label(node: Any, idx: int) -> str:
    action = str(getattr(node, "action", "") or "").strip()
    if action:
        return f"{idx}:{action}"
    outcome = str(getattr(node, "outcome", "") or "").strip()
    if outcome:
        return f"{idx}:{outcome}"
    conflict = str(getattr(node, "conflict", "") or "").strip()
    if conflict:
        return f"{idx}:{conflict}"
    return f"{idx}:event"


def build_narrative_chains(event_graph: EventGraph) -> Dict[str, Any]:
    nodes = event_graph.nodes or []
    edges = event_graph.edges or []

    adjacency: Dict[int, List[int]] = {idx: [] for idx in range(len(nodes))}
    indegree: Dict[int, int] = {idx: 0 for idx in range(len(nodes))}

    for edge in edges:
        try:
            src = int(edge.source)
            target = int(edge.target)
        except Exception:
            continue
        if 0 <= src < len(nodes) and 0 <= target < len(nodes):
            adjacency[src].append(target)
            indegree[target] += 1

    for idx in adjacency:
        adjacency[idx] = sorted(adjacency[idx])

    starts = [idx for idx in range(len(nodes)) if indegree[idx] == 0]
    if not starts:
        starts = list(range(len(nodes)))

    visited = set()
    chains: List[List[int]] = []

    for start in sorted(starts):
        if start in visited:
            continue
        chain: List[int] = []
        current = start
        while current not in visited:
            visited.add(current)
            chain.append(current)
            next_nodes = [n for n in adjacency[current] if n not in visited]
            if not next_nodes:
                break
            current = next_nodes[0]
        if chain:
            chains.append(chain)

    remaining = sorted(set(range(len(nodes))) - visited)
    for idx in remaining:
        chains.append([idx])

    chains = sorted(chains, key=lambda item: (item[0], len(item), tuple(item)))

    chain_payloads: List[Dict[str, Any]] = []
    confidences: List[float] = []
    for chain_idx, chain_nodes in enumerate(chains, start=1):
        chain_events = [_event_label(nodes[node_idx], node_idx) for node_idx in chain_nodes]
        chain_edges = sum(1 for node_idx in chain_nodes[:-1] if node_idx + 1 in chain_nodes[1:])
        base_confidence = 0.55 + (0.1 * min(1, len(chain_nodes) - 1)) + (0.1 * min(1, chain_edges))
        if any(getattr(nodes[node_idx], "conflict", "") for node_idx in chain_nodes):
            base_confidence += 0.1
        if any(getattr(nodes[node_idx], "outcome", "") for node_idx in chain_nodes):
            base_confidence += 0.1
        if len(chain_nodes) == 1:
            base_confidence = max(0.25, base_confidence - 0.1)
        confidence = round(min(0.99, base_confidence), 2)
        confidences.append(confidence)
        chain_payloads.append(
            {
                "chain_id": f"chain-{chain_idx:03d}",
                "events": chain_events,
                "length": len(chain_nodes),
                "start_event": chain_events[0] if chain_events else "",
                "end_event": chain_events[-1] if chain_events else "",
                "confidence": confidence,
            }
        )

    connected_nodes = {node_idx for edge in edges for node_idx in (getattr(edge, "source", None), getattr(edge, "target", None)) if isinstance(node_idx, int)}
    isolated_event_count = sum(1 for idx in range(len(nodes)) if idx not in connected_nodes)
    chain_count = len(chain_payloads)
    largest_chain_size = max((item["length"] for item in chain_payloads), default=0)
    average_chain_length = round((sum(item["length"] for item in chain_payloads) / chain_count), 2) if chain_count else 0.0
    chain_confidence = round((sum(confidences) / chain_count), 2) if chain_count else 0.0

    return {
        "chains": chain_payloads,
        "chain_count": chain_count,
        "largest_chain_size": largest_chain_size,
        "isolated_event_count": isolated_event_count,
        "average_chain_length": average_chain_length,
        "chain_confidence": chain_confidence,
        "diagnostics": {
            "chain_count": chain_count,
            "largest_chain_size": largest_chain_size,
            "isolated_event_count": isolated_event_count,
            "average_chain_length": average_chain_length,
            "chain_confidence": chain_confidence,
            "source": "runtime_v7_narrative_chain_builder",
        },
    }
