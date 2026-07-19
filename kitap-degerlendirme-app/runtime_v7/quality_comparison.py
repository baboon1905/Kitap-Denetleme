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


def compute_quality_comparison(production_quality: Dict[str, Any], shadow_quality: Dict[str, Any]) -> dict:
    production_metrics = production_quality or {}
    shadow_metrics = shadow_quality or {}
    theme_validation_delta = round(_normalize_value(shadow_metrics.get("theme_validation_coverage")) - _normalize_value(production_metrics.get("theme_validation_coverage")), 2)
    character_validation_delta = round(_normalize_value(shadow_metrics.get("character_validation_coverage")) - _normalize_value(production_metrics.get("character_validation_coverage")), 2)
    learning_outcome_validation_delta = round(_normalize_value(shadow_metrics.get("learning_outcome_validation_coverage")) - _normalize_value(production_metrics.get("learning_outcome_validation_coverage")), 2)
    coverage_delta = round(_normalize_value(shadow_metrics.get("overall_validation_coverage")) - _normalize_value(production_metrics.get("overall_validation_coverage")), 2)
    confidence_delta = round(_normalize_value(shadow_metrics.get("calibrated_overall_validation_confidence")) - _normalize_value(production_metrics.get("calibrated_overall_validation_confidence")), 2)
    overall_quality_delta = round((theme_validation_delta + character_validation_delta + learning_outcome_validation_delta + coverage_delta + confidence_delta) / 5.0, 2)
    improvement_detected = overall_quality_delta > 0.0

    return {
        "quality_comparison": {
            "theme_validation_delta": theme_validation_delta,
            "character_validation_delta": character_validation_delta,
            "learning_outcome_validation_delta": learning_outcome_validation_delta,
            "coverage_delta": coverage_delta,
            "confidence_delta": confidence_delta,
            "overall_quality_delta": overall_quality_delta,
        },
        "diagnostics": {
            "overall_quality_delta": overall_quality_delta,
            "quality_improvement_detected": improvement_detected,
            "comparison_confidence": round(max(0.0, min(1.0, 0.5 + overall_quality_delta)), 2),
        },
    }
