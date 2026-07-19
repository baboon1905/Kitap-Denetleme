from __future__ import annotations

from typing import Any, Dict, List


def _normalize_value_to_float(value: Any) -> float:
    if isinstance(value, (float, int)):
        value = float(value)
    elif isinstance(value, str):
        try:
            value = float(value.replace(",", "."))
        except Exception:
            value = 0.0
    else:
        value = 0.0

    if value is None:
        return 0.0
    try:
        value = float(value)
    except Exception:
        return 0.0

    if value > 1.0:
        value = value / 100.0
    return max(0.0, min(0.99, value))


def _normalize_learning_outcome_text(item: Any) -> str:
    if not isinstance(item, dict):
        return ""
    return str(
        item.get("kazanim")
        or item.get("learning_outcome")
        or item.get("description")
        or item.get("ad")
        or item.get("name")
        or ""
    ).strip()


def _count_outcome_evidence(item: Any) -> int:
    if not isinstance(item, dict):
        return 0
    evidence = item.get("kanitlar") or item.get("evidences") or item.get("evidence") or []
    if isinstance(evidence, dict):
        return 1
    if isinstance(evidence, list):
        return sum(1 for entry in evidence if isinstance(entry, (dict, str)))
    return 0


def _extract_learning_outcome_items(payload: dict) -> List[Dict[str, Any]]:
    outcomes: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for item in payload.get("kazanim_analizi") or []:
        if not isinstance(item, dict):
            continue
        name = _normalize_learning_outcome_text(item)
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        evidence_count = _count_outcome_evidence(item)
        confidence = _normalize_value_to_float(item.get("guven_skoru") or item.get("confidence") or 0.0)
        outcomes.append(
            {
                "learning_outcome": name,
                "evidence_count": evidence_count,
                "confidence": confidence,
            }
        )

    return outcomes


def _supported_by_primary_chain(
    outcome: Dict[str, Any],
    narrative_chains: Dict[str, Any],
) -> bool:
    if outcome.get("evidence_count", 0) <= 0:
        return False
    if not isinstance(narrative_chains, dict):
        return False
    chain_confidence = narrative_chains.get("chain_confidence", 0.0)
    chain_count = narrative_chains.get("chain_count", 0)
    return bool(chain_count >= 1 and chain_confidence >= 0.55)


def _supported_by_cause_effect(
    outcome: Dict[str, Any],
    cause_effect: Dict[str, Any],
) -> bool:
    if outcome.get("evidence_count", 0) <= 0:
        return False
    if not isinstance(cause_effect, dict):
        return False
    relations = cause_effect.get("cause_effect_relations")
    return bool(isinstance(relations, list) and len(relations) > 0)


def _supported_by_primary_conflict(
    outcome: Dict[str, Any],
    conflict_graph: Dict[str, Any],
    primary_conflict: Dict[str, Any],
) -> bool:
    if outcome.get("evidence_count", 0) <= 0:
        return False
    if not isinstance(conflict_graph, dict):
        return False
    conflicts = conflict_graph.get("conflicts")
    if isinstance(conflicts, list) and len(conflicts) > 0:
        return True
    if not isinstance(primary_conflict, dict):
        return False
    return bool(primary_conflict.get("participants") or primary_conflict.get("status"))


def _supported_by_resolution(
    outcome: Dict[str, Any],
    resolution: Dict[str, Any],
) -> bool:
    if outcome.get("evidence_count", 0) <= 0:
        return False
    if not isinstance(resolution, dict):
        return False
    status = str(resolution.get("status") or "").strip().lower()
    return status in {"resolved", "partially_resolved"}


def _compute_learning_outcome_confidence(
    outcome: Dict[str, Any],
    validation: Dict[str, bool],
) -> float:
    outcome_confidence = _normalize_value_to_float(outcome.get("confidence") or 0.0)
    support_score = sum(
        1 for key in (
            "supported_by_primary_chain",
            "supported_by_cause_effect",
            "supported_by_primary_conflict",
            "supported_by_resolution",
        )
        if validation.get(key)
    ) / 4.0
    base = support_score * 0.75 + outcome_confidence * 0.25
    if outcome.get("evidence_count", 0) == 0 and outcome_confidence <= 0.0:
        base = support_score * 0.5
    return round(min(0.99, base), 2)


def compute_learning_outcome_validation(
    payload: dict,
    narrative_chains: Dict[str, Any],
    cause_effect: Dict[str, Any],
    conflict_graph: Dict[str, Any],
    primary_conflict: Dict[str, Any],
    resolution: Dict[str, Any],
) -> dict:
    outcomes = _extract_learning_outcome_items(payload)
    validations: List[Dict[str, Any]] = []

    for outcome in outcomes:
        validation = {
            "supported_by_primary_chain": _supported_by_primary_chain(outcome, narrative_chains),
            "supported_by_cause_effect": _supported_by_cause_effect(outcome, cause_effect),
            "supported_by_primary_conflict": _supported_by_primary_conflict(outcome, conflict_graph, primary_conflict),
            "supported_by_resolution": _supported_by_resolution(outcome, resolution),
        }
        validation["confidence"] = _compute_learning_outcome_confidence(outcome, validation)
        validations.append({"learning_outcome": outcome["learning_outcome"], "validation": validation})

    supported_counts = {
        "validated_learning_outcome_count": len(validations),
        "primary_chain_supported_outcome_count": sum(1 for item in validations if item["validation"]["supported_by_primary_chain"]),
        "cause_effect_supported_outcome_count": sum(1 for item in validations if item["validation"]["supported_by_cause_effect"]),
        "conflict_supported_outcome_count": sum(1 for item in validations if item["validation"]["supported_by_primary_conflict"]),
        "resolution_supported_outcome_count": sum(1 for item in validations if item["validation"]["supported_by_resolution"]),
        "average_learning_outcome_validation_confidence": round(
            sum(item["validation"]["confidence"] for item in validations) / len(validations),
            2,
        ) if validations else 0.0,
    }

    return {
        "learning_outcome_validation": validations,
        "diagnostics": supported_counts,
    }
