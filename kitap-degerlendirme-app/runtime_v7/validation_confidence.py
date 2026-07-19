from __future__ import annotations

from typing import Any, Dict


def _normalize_value(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "."))
        except Exception:
            return 0.0
    return 0.0


def _confidence_band(overall_confidence: float) -> str:
    if overall_confidence >= 0.8:
        return "high"
    if overall_confidence >= 0.55:
        return "medium"
    if overall_confidence >= 0.25:
        return "low"
    return "insufficient"


def compute_validation_confidence(
    payload: dict,
    theme_validation_result: Dict[str, Any],
    character_validation_result: Dict[str, Any],
    learning_outcome_validation_result: Dict[str, Any],
) -> dict:
    theme_confidence = _normalize_value(
        (theme_validation_result.get("diagnostics") or {}).get("average_theme_validation_confidence")
    )
    character_confidence = _normalize_value(
        (character_validation_result.get("diagnostics") or {}).get("average_character_validation_confidence")
    )
    learning_outcome_confidence = _normalize_value(
        (learning_outcome_validation_result.get("diagnostics") or {}).get("average_learning_outcome_validation_confidence")
    )
    overall_confidence = round((theme_confidence + character_confidence + learning_outcome_confidence) / 3.0, 2)
    band = _confidence_band(overall_confidence)

    return {
        "validation_confidence": {
            "theme_confidence": round(theme_confidence, 2),
            "character_confidence": round(character_confidence, 2),
            "learning_outcome_confidence": round(learning_outcome_confidence, 2),
            "overall_confidence": overall_confidence,
            "confidence_band": band,
        },
        "diagnostics": {
            "calibrated_theme_validation_confidence": round(theme_confidence, 2),
            "calibrated_character_validation_confidence": round(character_confidence, 2),
            "calibrated_learning_outcome_validation_confidence": round(learning_outcome_confidence, 2),
            "calibrated_overall_validation_confidence": overall_confidence,
            "validation_confidence_band": band,
        },
    }
