from __future__ import annotations

from typing import Any, Dict, List

_ALLOWED_ACTIONS = {"keep_shadow", "expand_validation", "pilot_candidate", "hold"}


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


def _normalize_component_name(name: str) -> str:
    return (name or "").strip() or "Component"


def _action_for_candidate(candidate: Dict[str, Any]) -> str:
    status = (candidate.get("candidate_status") or "hold").strip().lower()
    readiness = (candidate.get("readiness") or "experimental").strip().lower()
    impact = (candidate.get("impact") or "insufficient_data").strip().lower()
    confidence = _clamp_conf(candidate.get("confidence") or 0.0)

    if status == "promote_candidate" and readiness == "ready" and impact in {"high", "medium"} and confidence >= 0.6:
        return "pilot_candidate"
    if status == "monitor" and readiness in {"needs_more_validation", "ready"} and impact in {"high", "medium"} and confidence >= 0.4:
        return "expand_validation"
    return "hold"


def generate_rollout_plan(
    payload: Dict[str, Any],
    promotion_candidates: Dict[str, Any],
    shadow_impact: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_items = (promotion_candidates or {}).get("candidates") or []
    if not isinstance(candidate_items, list):
        candidate_items = []

    steps: List[Dict[str, Any]] = []
    for index, candidate in enumerate(candidate_items, start=1):
        if not isinstance(candidate, dict):
            continue
        component = _normalize_component_name(candidate.get("component"))
        action = _action_for_candidate(candidate)
        confidence = _clamp_conf(candidate.get("confidence") or 0.0)
        reasons = candidate.get("reasons") or []
        if not isinstance(reasons, list):
            reasons = []
        reason_text = reasons[0] if reasons else "Deterministic rollout recommendation derived from promotion readiness and shadow impact signals."
        steps.append(
            {
                "step": index,
                "component": component,
                "action": action if action in _ALLOWED_ACTIONS else "hold",
                "reason": reason_text,
                "confidence": confidence,
            }
        )

    counts = {"pilot_candidate": 0, "expand_validation": 0, "hold": 0}
    for step in steps:
        action = step.get("action")
        if action in counts:
            counts[action] += 1

    recommended_next_action = "hold"
    if counts.get("pilot_candidate", 0) > 0:
        recommended_next_action = "pilot_candidate"
    elif counts.get("expand_validation", 0) > 0:
        recommended_next_action = "expand_validation"
    elif counts.get("hold", 0) > 0:
        recommended_next_action = "hold"

    diagnostics = {
        "rollout_step_count": len(steps),
        "pilot_candidate_count": counts.get("pilot_candidate", 0),
        "expand_validation_count": counts.get("expand_validation", 0),
        "hold_count": counts.get("hold", 0),
        "rollout_confidence": round(sum(step.get("confidence") or 0.0 for step in steps) / len(steps), 2) if steps else 0.0,
        "source": "runtime_v7_rollout_plan",
    }

    return {
        "rollout_plan": {
            "steps": steps,
            "recommended_next_action": recommended_next_action,
            "diagnostics": diagnostics,
        }
    }
