from __future__ import annotations

from typing import Any, Dict, List

_ALLOWED_STATUSES = {"promote_candidate", "monitor", "hold"}


def _clamp_conf(value: Any) -> float:
    try:
        value = float(value)
    except Exception:
        value = 0.0
    if value < 0.0:
        value = 0.0
    if value > 0.99:
        value = 0.99
    return round(value, 2)


def _classify_candidate(component: str, readiness: str, impact: str, confidence: float) -> str:
    readiness_norm = (readiness or "").strip().lower()
    impact_norm = (impact or "").strip().lower()
    conf = _clamp_conf(confidence)

    if readiness_norm == "ready" and impact_norm in {"high", "medium"} and conf >= 0.6:
        return "promote_candidate"
    if readiness_norm in {"needs_more_validation", "experimental"} and impact_norm in {"high", "medium"} and conf >= 0.4:
        return "monitor"
    return "hold"


def generate_promotion_candidates(
    payload: Dict[str, Any],
    shadow_impact: Dict[str, Any],
    promotion_readiness: Dict[str, Any],
) -> Dict[str, Any]:
    impact_components = (shadow_impact or {}).get("components") or []
    readiness_components = (promotion_readiness or {}).get("components") or []

    # deterministic component mapping by name; no title-specific heuristics
    ready_lookup = {item.get("name"): item for item in readiness_components if isinstance(item, dict) and item.get("name")}
    impact_lookup = {item.get("name"): item for item in impact_components if isinstance(item, dict) and item.get("name")}

    candidates: List[Dict[str, Any]] = []
    for name in [
        "Theme Validation",
        "Character Validation",
        "Learning Outcome Validation",
        "Validation Coverage",
        "Validation Confidence",
        "Quality Comparison",
        "Recommendation Engine",
        "Promotion Readiness",
    ]:
        readiness = (ready_lookup.get(name) or {}).get("readiness") or "experimental"
        impact = (impact_lookup.get(name) or {}).get("estimated_impact") or "insufficient_data"
        confidence = (impact_lookup.get(name) or {}).get("confidence") or 0.0
        candidate_status = _classify_candidate(name, readiness, impact, confidence)
        reasons = []
        if candidate_status == "promote_candidate":
            reasons.append("High readiness and meaningful estimated impact.")
        elif candidate_status == "monitor":
            reasons.append("Moderate readiness but still needs closer review.")
        else:
            reasons.append("The component is not yet strong enough for promotion.")
        reasons.append("The decision is driven by deterministic readiness and impact signals.")
        candidates.append(
            {
                "component": name,
                "candidate_status": candidate_status if candidate_status in _ALLOWED_STATUSES else "hold",
                "readiness": readiness,
                "impact": impact,
                "confidence": _clamp_conf(confidence),
                "reasons": reasons,
            }
        )

    counts = {"promote_candidate": 0, "monitor": 0, "hold": 0}
    for candidate in candidates:
        status = candidate.get("candidate_status")
        if status in counts:
            counts[status] += 1

    diagnostics = {
        "promote_candidate_count": counts.get("promote_candidate", 0),
        "monitor_candidate_count": counts.get("monitor", 0),
        "hold_candidate_count": counts.get("hold", 0),
        "promotion_candidate_confidence": round(sum(item.get("confidence") or 0.0 for item in candidates) / len(candidates), 2) if candidates else 0.0,
        "source": "runtime_v7_promotion_candidates",
    }

    return {
        "promotion_candidates": {
            "candidates": candidates,
            "promote_candidate_count": counts.get("promote_candidate", 0),
            "monitor_count": counts.get("monitor", 0),
            "hold_count": counts.get("hold", 0),
            "diagnostics": diagnostics,
        }
    }
