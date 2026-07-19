from __future__ import annotations

from typing import Any, Dict, List


def build_cause_effect_relations(narrative_chains: Dict[str, Any]) -> Dict[str, Any]:
    chains = narrative_chains.get("chains") or []
    if not isinstance(chains, list) or not chains:
        return {
            "cause_effect_relations": [],
            "diagnostics": {
                "cause_effect_count": 0,
                "average_cause_effect_confidence": 0.0,
                "weak_causal_reason": "no_chains",
            },
        }

    relations: List[Dict[str, Any]] = []
    confidences: List[float] = []

    for chain in chains:
        events = chain.get("events") or []
        if not isinstance(events, list) or len(events) < 2:
            continue
        for idx in range(len(events) - 1):
            cause_event = events[idx]
            effect_event = events[idx + 1]
            confidence = round(min(0.99, 0.55 + (0.08 * (idx + 1))), 2)
            relations.append(
                {
                    "cause_event_id": cause_event,
                    "effect_event_id": effect_event,
                    "relation_type": "sequential_inference",
                    "confidence": confidence,
                }
            )
            confidences.append(confidence)

    if not relations:
        return {
            "cause_effect_relations": [],
            "diagnostics": {
                "cause_effect_count": 0,
                "average_cause_effect_confidence": 0.0,
                "weak_causal_reason": "insufficient_events",
            },
        }

    average_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    if average_confidence < 0.6:
        weak_reason = "low_relation_confidence"
    else:
        weak_reason = "sufficient"

    return {
        "cause_effect_relations": relations,
        "diagnostics": {
            "cause_effect_count": len(relations),
            "average_cause_effect_confidence": average_confidence,
            "weak_causal_reason": weak_reason,
        },
    }
