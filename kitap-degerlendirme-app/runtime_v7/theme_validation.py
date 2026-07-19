from __future__ import annotations

from typing import Any, Dict, List, Optional


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


def _normalize_theme_name(item: Any) -> str:
    if not isinstance(item, dict):
        return ""
    name = str(
        item.get("ad")
        or item.get("tema")
        or item.get("name")
        or item.get("label")
        or ""
    ).strip()
    return name


def _count_theme_evidence(item: Any) -> int:
    if not isinstance(item, dict):
        return 0
    evidence = item.get("kanitlar") or item.get("evidences") or item.get("evidence") or []
    if isinstance(evidence, dict):
        return 1
    if isinstance(evidence, list):
        return sum(1 for entry in evidence if isinstance(entry, dict) or isinstance(entry, str))
    return 0


def _theme_confidence_value(item: Any) -> float:
    if not isinstance(item, dict):
        return 0.0
    confidence = item.get("guven_skoru")
    if confidence is None:
        confidence = item.get("tema_guven_skoru")
    if confidence is None:
        confidence = item.get("confidence")
    if confidence is None:
        confidence = item.get("tema_gucu")
    return _normalize_value_to_float(confidence)


def _extract_theme_items(payload: dict) -> List[Dict[str, Any]]:
    themes: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for item in payload.get("tema_analizi") or []:
        if not isinstance(item, dict):
            continue
        name = _normalize_theme_name(item)
        if not name or name in seen:
            continue
        seen.add(name)
        themes.append(
            {
                "name": name,
                "evidence_count": _count_theme_evidence(item),
                "confidence": _theme_confidence_value(item),
            }
        )

    if not themes:
        for item in payload.get("ilk_uc_baskin_tema") or []:
            if isinstance(item, dict):
                name = _normalize_theme_name(item)
            elif isinstance(item, str):
                name = item.strip()
            else:
                name = ""
            if not name or name in seen:
                continue
            seen.add(name)
            themes.append({"name": name, "evidence_count": 0, "confidence": 0.0})

    return themes


def _supported_by_primary_chain(theme: dict, narrative_chains: dict) -> bool:
    if theme.get("evidence_count", 0) <= 0:
        return False
    chain_confidence = narrative_chains.get("chain_confidence", 0.0) if isinstance(narrative_chains, dict) else 0.0
    chain_count = narrative_chains.get("chain_count", 0) if isinstance(narrative_chains, dict) else 0
    return bool(chain_count >= 1 and chain_confidence >= 0.55)


def _supported_by_cause_effect(theme: dict, cause_effect: dict) -> bool:
    if theme.get("evidence_count", 0) <= 0:
        return False
    relations = cause_effect.get("cause_effect_relations") if isinstance(cause_effect, dict) else []
    return bool(isinstance(relations, list) and len(relations) > 0)


def _supported_by_conflict(theme: dict, conflict_graph: dict) -> bool:
    if theme.get("evidence_count", 0) <= 0:
        return False
    conflicts = conflict_graph.get("conflicts") if isinstance(conflict_graph, dict) else []
    return bool(isinstance(conflicts, list) and len(conflicts) > 0)


def _supported_by_resolution(theme: dict, resolution: dict) -> bool:
    if theme.get("evidence_count", 0) <= 0:
        return False
    if not isinstance(resolution, dict):
        return False
    status = str(resolution.get("status") or "").strip().lower()
    return status in {"resolved", "partially_resolved"}


def _compute_theme_confidence(theme: dict, validation: dict) -> float:
    theme_confidence = theme.get("confidence", 0.0)
    support_score = sum(
        1 for key in (
            "supported_by_primary_chain",
            "supported_by_cause_effect",
            "supported_by_conflict",
            "supported_by_resolution",
        )
        if validation.get(key)
    ) / 4.0
    confidence = min(0.99, support_score * 0.75 + theme_confidence * 0.25)
    if theme.get("evidence_count", 0) == 0:
        confidence = min(0.99, theme_confidence * 0.5)
    return round(confidence, 2)


def compute_theme_validation(
    payload: dict,
    narrative_chains: dict,
    cause_effect: dict,
    conflict_graph: dict,
    resolution: dict,
) -> dict:
    themes = _extract_theme_items(payload)
    validations: List[Dict[str, Any]] = []

    for theme in themes:
        validation = {
            "supported_by_primary_chain": _supported_by_primary_chain(theme, narrative_chains),
            "supported_by_cause_effect": _supported_by_cause_effect(theme, cause_effect),
            "supported_by_conflict": _supported_by_conflict(theme, conflict_graph),
            "supported_by_resolution": _supported_by_resolution(theme, resolution),
        }
        validation["confidence"] = _compute_theme_confidence(theme, validation)
        validations.append({"theme": theme["name"], "validation": validation})

    supported_counts = {
        "validated_theme_count": len(validations),
        "primary_chain_supported_theme_count": sum(1 for item in validations if item["validation"]["supported_by_primary_chain"]),
        "conflict_supported_theme_count": sum(1 for item in validations if item["validation"]["supported_by_conflict"]),
        "resolution_supported_theme_count": sum(1 for item in validations if item["validation"]["supported_by_resolution"]),
        "average_theme_validation_confidence": round(
            sum(item["validation"]["confidence"] for item in validations) / len(validations),
            2,
        ) if validations else 0.0,
    }

    return {
        "theme_validation": validations,
        "diagnostics": supported_counts,
    }
