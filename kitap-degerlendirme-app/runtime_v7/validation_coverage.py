from __future__ import annotations

from typing import Any, Dict, List


def _count_source_items(payload: dict, field_name: str) -> int:
    if field_name == "theme":
        for candidate in ("tema_analizi", "ilk_uc_baskin_tema"):
            items = payload.get(candidate)
            if isinstance(items, list):
                return sum(1 for item in items if isinstance(item, dict) or isinstance(item, str))
        return 0
    if field_name == "character":
        items = payload.get("ana_karakterler")
        if isinstance(items, list):
            return sum(1 for item in items if isinstance(item, dict) or isinstance(item, str))
        return 0
    if field_name == "learning_outcome":
        items = payload.get("kazanim_analizi")
        if isinstance(items, list):
            return sum(1 for item in items if isinstance(item, dict) or isinstance(item, str))
        return 0
    return 0


def _extract_validation_items(validation_result: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    items = validation_result.get(key) if isinstance(validation_result, dict) else []
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


def _has_support(validation_item: Dict[str, Any]) -> bool:
    validation = validation_item.get("validation") if isinstance(validation_item, dict) else {}
    if not isinstance(validation, dict):
        return False
    if validation.get("supported_by_primary_chain"):
        return True
    if validation.get("supported_by_cause_effect"):
        return True
    if validation.get("supported_by_conflict"):
        return True
    if validation.get("supported_by_primary_conflict"):
        return True
    if validation.get("supported_by_resolution"):
        return True
    confidence = validation.get("confidence", 0.0)
    try:
        return float(confidence) >= 0.6
    except Exception:
        return False


def _compute_category_coverage(source_item_count: int, validation_items: List[Dict[str, Any]]) -> float:
    if source_item_count <= 0:
        return 0.0
    supported = sum(1 for item in validation_items if _has_support(item))
    return round(supported / float(source_item_count), 2)


def _build_coverage_reasons(theme_coverage: float, character_coverage: float, learning_outcome_coverage: float, theme_count: int, character_count: int, learning_outcome_count: int) -> List[str]:
    reasons: List[str] = []
    if theme_count <= 0 or character_count <= 0 or learning_outcome_count <= 0:
        reasons.append("insufficient_source_items")
    if learning_outcome_count <= 0:
        reasons.append("missing_learning_outcomes")
    if character_count <= 1 or character_coverage <= 0.5:
        reasons.append("sparse_character_graph")
    if theme_coverage < 0.5 or character_coverage < 0.5 or learning_outcome_coverage < 0.5:
        reasons.append("weak_narrative_support")
    if not reasons:
        reasons.append("sufficient")
    return list(dict.fromkeys(reasons))


def _pick_weak_reason(reasons: List[str]) -> str:
    priority = [
        "missing_learning_outcomes",
        "sparse_character_graph",
        "insufficient_source_items",
        "weak_narrative_support",
        "sufficient",
    ]
    for candidate in priority:
        if candidate in reasons:
            return candidate
    return "sufficient"


def compute_validation_coverage(
    payload: dict,
    theme_validation_result: Dict[str, Any],
    character_validation_result: Dict[str, Any],
    learning_outcome_validation_result: Dict[str, Any],
) -> dict:
    theme_count = _count_source_items(payload, "theme")
    character_count = _count_source_items(payload, "character")
    learning_outcome_count = _count_source_items(payload, "learning_outcome")

    theme_items = _extract_validation_items(theme_validation_result, "theme_validation")
    character_items = _extract_validation_items(character_validation_result, "character_validation")
    learning_outcome_items = _extract_validation_items(learning_outcome_validation_result, "learning_outcome_validation")

    theme_coverage = _compute_category_coverage(theme_count, theme_items)
    character_coverage = _compute_category_coverage(character_count, character_items)
    learning_outcome_coverage = _compute_category_coverage(learning_outcome_count, learning_outcome_items)
    overall_coverage = round((theme_coverage + character_coverage + learning_outcome_coverage) / 3.0, 2)

    coverage_reasons = _build_coverage_reasons(
        theme_coverage,
        character_coverage,
        learning_outcome_coverage,
        theme_count,
        character_count,
        learning_outcome_count,
    )
    weak_reason = _pick_weak_reason(coverage_reasons)

    return {
        "validation_coverage": {
            "theme_coverage": theme_coverage,
            "character_coverage": character_coverage,
            "learning_outcome_coverage": learning_outcome_coverage,
            "overall_coverage": overall_coverage,
            "coverage_reasons": coverage_reasons,
        },
        "diagnostics": {
            "theme_validation_coverage": theme_coverage,
            "character_validation_coverage": character_coverage,
            "learning_outcome_validation_coverage": learning_outcome_coverage,
            "overall_validation_coverage": overall_coverage,
            "weak_validation_coverage_reason": weak_reason,
        },
    }
