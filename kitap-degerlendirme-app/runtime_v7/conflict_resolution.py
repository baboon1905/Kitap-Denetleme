from __future__ import annotations

from typing import Any, Dict, Optional


def _extract_resolution_text(story_arc: Optional[Dict[str, Any]], narrative_graph: Optional[Dict[str, Any]] = None) -> str:
    if isinstance(story_arc, dict):
        stages = story_arc.get("stages") or {}
        if isinstance(stages, dict):
            for key in ("resolution", "outcome", "result", "resolved", "sonuc", "cozum"):
                value = stages.get(key)
                if value:
                    return str(value)
        elif isinstance(stages, list):
            for value in stages:
                if value:
                    return str(value)
    if isinstance(narrative_graph, dict):
        resolution_links = narrative_graph.get("resolution_links") or []
        if isinstance(resolution_links, list):
            for item in resolution_links:
                if isinstance(item, dict):
                    outcome = item.get("outcome") or item.get("result") or item.get("resolution")
                    if outcome:
                        return str(outcome)
    return ""


def _determine_resolution_status(
    conflict: Optional[Dict[str, Any]],
    cause_effect_relations: list,
    chain_confidence: float,
) -> tuple[str, float]:
    """
    Algorithmically determine resolution status and confidence.
    
    Rules (no book-specific heuristics):
    - resolved: conflict has explicit outcome AND chain is complete
    - partially_resolved: outcome exists but chain/causality is weak
    - unresolved: no outcome or weak chain connection
    - ambiguous: conflicting signals
    """
    if not conflict:
        return "unresolved", 0.0
    
    has_outcome = conflict.get("resolved", False)
    conflict_confidence = conflict.get("confidence", 0.0)
    
    # No explicit outcome
    if not has_outcome:
        return "unresolved", conflict_confidence
    
    # Has outcome, check chain/causality strength
    has_cause_effect = bool(cause_effect_relations)
    chain_strength = chain_confidence if chain_confidence else 0.0
    
    # Strong chain with outcome = resolved
    if has_cause_effect and chain_strength >= 0.75:
        resolution_confidence = round(min(0.99, (conflict_confidence + chain_strength) / 2), 2)
        return "resolved", resolution_confidence
    
    # Outcome exists but weak chain = partially_resolved
    if has_outcome and chain_strength < 0.75:
        resolution_confidence = round(min(0.99, conflict_confidence * 0.8), 2)
        return "partially_resolved", resolution_confidence
    
    # Outcome with some causality but not strong
    if has_outcome and has_cause_effect:
        resolution_confidence = round(min(0.99, (conflict_confidence + chain_strength) / 2), 2)
        return "partially_resolved", resolution_confidence
    
    # Outcome but no causality structure
    if has_outcome:
        resolution_confidence = round(conflict_confidence * 0.7, 2)
        return "partially_resolved", resolution_confidence
    
    return "ambiguous", conflict_confidence


def build_primary_conflict_resolution(
    conflict_graph: Dict[str, Any],
    narrative_chains: Optional[Dict[str, Any]] = None,
    cause_effect: Optional[Dict[str, Any]] = None,
    story_arc: Optional[Dict[str, Any]] = None,
    narrative_graph: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build primary conflict and resolution state from conflict graph.
    
    Output structure:
    {
        "primary_conflict": {
            "conflict_id": "...",
            "confidence": 0.xx,
            "participants": [...],
            "related_events": [...],
            "conflict_type": "..."
        },
        "resolution": {
            "status": "resolved | partially_resolved | unresolved | ambiguous",
            "confidence": 0.xx
        },
        "diagnostics": {
            "resolution_status": "...",
            "resolution_confidence": 0.xx,
            "conflict_resolution_score": 0.xx,
            "unresolved_major_conflicts": 0,
            "weak_resolution_reason": "...",
            "source": "runtime_v7_conflict_resolution"
        }
    }
    """
    conflicts = conflict_graph.get("conflicts") or []
    conflict_diagnostics = conflict_graph.get("diagnostics") or {}
    
    chains = (narrative_chains or {}).get("chains") or []
    chain_confidence = (narrative_chains or {}).get("chain_confidence", 0.0)
    
    cause_effect_relations = (cause_effect or {}).get("cause_effect_relations") or []
    
    # Extract primary conflict (first/main conflict)
    primary_conflict_data = None
    if conflicts:
        conflict = conflicts[0]
        primary_conflict_data = {
            "conflict_id": conflict.get("conflict_id") or "conflict-001",
            "confidence": conflict.get("confidence", 0.0),
            "participants": conflict.get("participants") or [],
            "related_events": conflict.get("related_events") or [],
            "conflict_type": conflict.get("conflict_type") or "unknown",
        }
    
    # Determine resolution status
    resolution_status, resolution_confidence = _determine_resolution_status(
        primary_conflict_data,
        cause_effect_relations,
        chain_confidence,
    )
    
    # Calculate conflict resolution score
    if primary_conflict_data:
        conflict_confidence = primary_conflict_data.get("confidence", 0.0)
        conflict_resolution_score = round(
            (conflict_confidence * 0.5 + resolution_confidence * 0.5),
            2
        )
    else:
        conflict_resolution_score = 0.0
    
    # Determine weak resolution reason (only general rules)
    unresolved_count = conflict_diagnostics.get("unresolved_conflict_count", 0)
    weak_reason = "sufficient"
    
    if not conflicts:
        weak_reason = "insufficient_conflict_data"
    elif resolution_confidence < 0.6:
        weak_reason = "low_resolution_confidence"
    elif len(chains) > 2:
        weak_reason = "fragmented_conflict_graph"
    
    resolution_text = _extract_resolution_text(story_arc, narrative_graph)
    diagnostics = {
        "primary_conflict_detected": bool(primary_conflict_data),
        "resolution_detected": bool(resolution_text or resolution_status != "unresolved"),
        "resolution_status": resolution_status,
        "resolution_confidence": resolution_confidence,
        "conflict_resolution_score": conflict_resolution_score,
        "unresolved_major_conflicts": unresolved_count,
        "weak_resolution_reason": weak_reason,
        "source": "runtime_v7_conflict_resolution",
    }
    
    return {
        "primary_conflict": primary_conflict_data,
        "resolution": {
            "status": resolution_status,
            "confidence": resolution_confidence,
            "resolution_text": resolution_text,
        },
        "diagnostics": diagnostics,
    }


def build_conflict_resolution(event_graph: Any, narrative_graph: Any, story_arc: Any, conflict_graph: Any) -> Dict[str, Any]:
    """Backward-compatible wrapper for the legacy conflict-resolution API."""
    return build_primary_conflict_resolution(
        conflict_graph if isinstance(conflict_graph, dict) else {},
        narrative_chains=narrative_graph if isinstance(narrative_graph, dict) else None,
        cause_effect=story_arc if isinstance(story_arc, dict) else None,
        story_arc=story_arc if isinstance(story_arc, dict) else None,
        narrative_graph=narrative_graph if isinstance(narrative_graph, dict) else None,
    )
