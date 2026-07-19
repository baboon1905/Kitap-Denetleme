from __future__ import annotations

from typing import Any, Dict, List, Optional


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


def _normalize_participants(node: Any) -> List[str]:
    actors = getattr(node, "actors", []) or []
    if isinstance(actors, str):
        actors = [actors]
    if not isinstance(actors, list):
        actors = []

    participants: List[str] = []
    for actor in actors:
        if not isinstance(actor, str):
            continue
        value = actor.strip()
        if value and value not in participants:
            participants.append(value)
    return participants


def _extract_event_index(event_id: Any) -> Optional[int]:
    if not isinstance(event_id, str):
        return None
    candidate = event_id.split(":", 1)[0].strip()
    try:
        return int(candidate)
    except ValueError:
        return None


def _infer_conflict_type(participants: List[str], explicit_conflict: bool, cause_effect_present: bool) -> str:
    if explicit_conflict and len(participants) >= 2:
        return "direct_confrontation"
    if len(participants) >= 2:
        return "interpersonal_tension"
    if cause_effect_present:
        return "narrative_tension"
    return "obstacle"


def build_conflict_graph(
    event_graph: Any,
    narrative_chains: Optional[Dict[str, Any]] = None,
    cause_effect: Optional[Dict[str, Any]] = None,
    narrative_graph: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    nodes = getattr(event_graph, "nodes", []) or []
    if not isinstance(nodes, list):
        nodes = []

    conflict_links = []
    if isinstance(narrative_graph, dict):
        conflict_links = narrative_graph.get("conflict_links") or []

    chains = (narrative_chains or {}).get("chains") or []
    cause_effect_relations = (cause_effect or {}).get("cause_effect_relations") or []
    chain_confidence = (narrative_chains or {}).get("chain_confidence", 0.0)
    chain_count = (narrative_chains or {}).get("chain_count", 0)
    isolated_event_count = (narrative_chains or {}).get("isolated_event_count", 0)

    conflicts: List[Dict[str, Any]] = []
    confidences: List[float] = []

    seeded_candidates: List[Dict[str, Any]] = []
    for entry in conflict_links:
        if not isinstance(entry, dict):
            continue
        node_idx = entry.get("node")
        try:
            node_idx = int(node_idx)
        except Exception:
            continue
        if 0 <= node_idx < len(nodes):
            seeded_candidates.append({"node_idx": node_idx, "source": "narrative_graph"})

    if not seeded_candidates:
        explicit_conflict_nodes = [
            idx for idx, node in enumerate(nodes)
            if str(getattr(node, "conflict", "") or "").strip()
        ]
        if explicit_conflict_nodes:
            seeded_candidates.append({"node_idx": explicit_conflict_nodes[0], "source": "explicit_conflict"})
        elif cause_effect_relations:
            for relation in cause_effect_relations:
                if not isinstance(relation, dict):
                    continue
                cause_event_id = relation.get("cause_event_id")
                effect_event_id = relation.get("effect_event_id")
                cause_idx = _extract_event_index(cause_event_id)
                effect_idx = _extract_event_index(effect_event_id)
                if cause_idx is not None and 0 <= cause_idx < len(nodes):
                    seeded_candidates.append({"node_idx": cause_idx, "source": "cause_effect"})
                    break
                if effect_idx is not None and 0 <= effect_idx < len(nodes):
                    seeded_candidates.append({"node_idx": effect_idx, "source": "cause_effect"})
                    break

    if not seeded_candidates and nodes:
        seeded_candidates.append({"node_idx": 0, "source": "fallback"})

    if seeded_candidates:
        candidate = seeded_candidates[0]
        node_idx = candidate.get("node_idx")
        if isinstance(node_idx, int) and 0 <= node_idx < len(nodes):
            node = nodes[node_idx]
            explicit_conflict = bool(str(getattr(node, "conflict", "") or "").strip())
            participants = _normalize_participants(node)

            related_events = []
            for chain in chains:
                if not isinstance(chain, dict):
                    continue
                chain_events = chain.get("events") or []
                if not isinstance(chain_events, list):
                    continue
                for event_label in chain_events:
                    event_index = _extract_event_index(event_label)
                    if event_index == node_idx:
                        related_events.append(event_label)
                        break
            if not related_events:
                related_events = [_event_label(node, node_idx)]

            confidence_base = 0.55
            if explicit_conflict:
                confidence_base += 0.15
            if cause_effect_relations:
                confidence_base += 0.1
            if chain_confidence:
                confidence_base += min(0.1, max(0.0, chain_confidence * 0.1))
            if participants:
                confidence_base += 0.05
            confidence = round(min(0.99, confidence_base), 2)
            confidences.append(confidence)

            conflicts.append(
                {
                    "conflict_id": "conflict-001",
                    "participants": participants,
                    "related_events": related_events,
                    "conflict_type": _infer_conflict_type(participants, explicit_conflict, bool(cause_effect_relations)),
                    "confidence": confidence,
                    "resolved": bool(str(getattr(node, "outcome", "") or "").strip()),
                }
            )

    if not conflicts:
        return {
            "conflicts": [],
            "diagnostics": {
                "conflict_count": 0,
                "primary_conflict_confidence": 0.0,
                "conflict_density": 0.0,
                "unresolved_conflict_count": 0,
                "weak_conflict_reason": "no_conflicts",
                "source": "runtime_v7_conflict_graph_builder",
            },
        }

    primary_conflict_confidence = round(max(confidences), 2) if confidences else 0.0
    conflict_density = round(len(conflicts) / max(1, len(nodes)), 2) if nodes else 0.0
    unresolved_conflict_count = sum(1 for conflict in conflicts if not conflict.get("resolved", False))
    if not cause_effect_relations:
        weak_reason = "isolated_events" if isolated_event_count else "weak_causality"
    elif primary_conflict_confidence < 0.6:
        weak_reason = "weak_causality"
    elif chain_count > 2 or isolated_event_count > 0:
        weak_reason = "fragmented_narrative"
    else:
        weak_reason = "sufficient"

    return {
        "conflicts": conflicts,
        "diagnostics": {
            "conflict_count": len(conflicts),
            "primary_conflict_confidence": primary_conflict_confidence,
            "conflict_density": conflict_density,
            "unresolved_conflict_count": unresolved_conflict_count,
            "weak_conflict_reason": weak_reason,
            "source": "runtime_v7_conflict_graph_builder",
        },
    }
