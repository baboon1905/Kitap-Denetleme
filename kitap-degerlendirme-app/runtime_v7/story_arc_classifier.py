from __future__ import annotations

from typing import Any, Dict, List, Optional

ALLOWED_ARC_TYPES = {
    "journey",
    "discovery",
    "transformation",
    "conflict_resolution",
    "episodic",
    "informational",
    "ambiguous",
}


def _normalize_signal(signal: str) -> str:
    return str(signal or "").strip().lower()


def _count_non_empty(values: List[Any]) -> int:
    return sum(1 for item in values if item)


def _choose_arc_type(signals: List[str]) -> str:
    counts = {arc_type: 0 for arc_type in ALLOWED_ARC_TYPES}
    for signal in signals:
        normalized = _normalize_signal(signal)
        if normalized in counts:
            counts[normalized] += 1
    if not any(counts.values()):
        return "ambiguous"
    chosen = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
    return chosen


def _estimate_confidence(signal_count: int, chain_confidence: float, conflict_confidence: float) -> float:
    if signal_count <= 0:
        return 0.0
    base = min(0.85, 0.25 + 0.2 * signal_count)
    base += 0.1 * min(1.0, chain_confidence)
    base += 0.05 * min(1.0, conflict_confidence)
    return round(min(0.99, base), 2)


def _map_arc_signals(
    story_arc: dict,
    narrative_chains: dict,
    cause_effect: dict,
    conflict_graph: dict,
    resolution: dict,
) -> List[str]:
    signals: List[str] = []

    if story_arc.get("type") == "complex":
        signals.append("journey")
    if story_arc.get("type") == "linear":
        signals.append("episodic")

    if isinstance(story_arc.get("stages"), dict):
        stage_text = " ".join(str(value) for value in story_arc["stages"].values() if value)
        if "discovery" in stage_text.lower() or "find" in stage_text.lower() or "learn" in stage_text.lower():
            signals.append("discovery")
        if "transform" in stage_text.lower() or "change" in stage_text.lower() or "growth" in stage_text.lower():
            signals.append("transformation")
        if "conflict" in stage_text.lower() or "resolution" in stage_text.lower() or "climax" in stage_text.lower():
            signals.append("conflict_resolution")

    if isinstance(narrative_chains.get("chains"), list) and len(narrative_chains["chains"]) >= 2:
        signals.append("episodic")

    if narrative_chains.get("chain_confidence", 0.0) > 0.75:
        signals.append("journey")

    if cause_effect.get("cause_effect_relations"):
        signals.append("informational")

    if conflict_graph.get("conflicts"):
        signals.append("conflict_resolution")

    if resolution.get("status") in {"resolved", "partially_resolved"}:
        signals.append("conflict_resolution")

    return [signal for signal in signals if signal in ALLOWED_ARC_TYPES]


def build_story_arc_classification(
    story_arc: dict,
    narrative_chains: dict,
    cause_effect: dict,
    conflict_graph: dict,
    resolution: dict,
) -> Dict[str, Any]:
    signals = _map_arc_signals(story_arc, narrative_chains, cause_effect, conflict_graph, resolution)
    signal_count = len(signals)
    arc_type = _choose_arc_type(signals)
    confidence = _estimate_confidence(signal_count, narrative_chains.get("chain_confidence", 0.0), resolution.get("confidence", 0.0))

    weak_reason = "sufficient"
    if signal_count == 0:
        weak_reason = "insufficient_narrative_data"
    elif len(set(signals)) > 1 and arc_type == "ambiguous":
        weak_reason = "conflicting_signals"
    elif confidence < 0.5:
        weak_reason = "low_confidence"

    return {
        "story_arc_classification": {
            "arc_type": arc_type,
            "confidence": confidence,
            "signals": signals,
        },
        "diagnostics": {
            "classified_arc_type": arc_type,
            "arc_classification_confidence": confidence,
            "arc_signal_count": signal_count,
            "weak_arc_classification_reason": weak_reason,
            "source": "runtime_v7_story_arc_classifier",
        },
    }
