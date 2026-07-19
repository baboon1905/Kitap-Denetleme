from __future__ import annotations

from typing import Any, Dict, List, Tuple


_ALLOWED_IMPACTS = {"high", "medium", "low", "insufficient_data"}


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


def _clamp_cov(value: Any) -> float:
    try:
        value = float(value)
    except Exception:
        value = 0.0
    if value < 0.0:
        value = 0.0
    if value > 1.0:
        value = 1.0
    return round(value, 2)


def _impact_score(impact: str) -> int:
    mapping = {"high": 3, "medium": 2, "low": 1, "insufficient_data": 0}
    return mapping.get(impact, 0)


def _impact_from_signal(confidence: float, coverage: float = 1.0, *, fallback: str = "insufficient_data") -> str:
    conf = _clamp_conf(confidence)
    cov = _clamp_cov(coverage)
    if conf <= 0.0 and cov <= 0.0:
        return fallback
    if conf >= 0.75 and cov >= 0.75:
        return "high"
    if conf >= 0.55 and cov >= 0.55:
        return "medium"
    if conf >= 0.3:
        return "low"
    return "low"


def _build_component(name: str, impact: str, confidence: float, reasons: List[str]) -> Dict[str, Any]:
    impact = impact if impact in _ALLOWED_IMPACTS else "insufficient_data"
    return {
        "name": name,
        "estimated_impact": impact,
        "confidence": _clamp_conf(confidence),
        "reasons": reasons,
    }


def generate_shadow_impact(
    payload: Dict[str, Any],
    theme_validation: Dict[str, Any],
    character_validation: Dict[str, Any],
    learning_outcome_validation: Dict[str, Any],
    validation_coverage: Dict[str, Any],
    validation_confidence: Dict[str, Any],
    quality_comparison: Dict[str, Any],
    recommendations: Dict[str, Any],
    promotion_readiness: Dict[str, Any],
) -> Dict[str, Any]:
    components: List[Dict[str, Any]] = []

    theme_diag = (theme_validation or {}).get("diagnostics") or {}
    theme_conf = (theme_validation or {}).get("diagnostics", {}).get("average_theme_validation_confidence") or theme_diag.get("average_theme_validation_confidence") or 0.0
    theme_cov = (validation_coverage or {}).get("diagnostics", {}).get("theme_validation_coverage") or 0.0
    theme_impact = _impact_from_signal(theme_conf, theme_cov)
    components.append(
        _build_component(
            "Theme Validation",
            theme_impact,
            theme_conf,
            [
                "Uses confidence and coverage signals from the theme validation layer.",
                "The assessment remains deterministic and does not depend on title-specific branching.",
            ],
        )
    )

    character_diag = (character_validation or {}).get("diagnostics") or {}
    character_conf = character_diag.get("average_character_validation_confidence") or 0.0
    character_cov = (validation_coverage or {}).get("diagnostics", {}).get("character_validation_coverage") or 0.0
    character_impact = _impact_from_signal(character_conf, character_cov)
    components.append(
        _build_component(
            "Character Validation",
            character_impact,
            character_conf,
            [
                "Uses confidence and coverage signals from the character validation layer.",
                "The assessment remains deterministic and does not depend on title-specific branching.",
            ],
        )
    )

    learning_diag = (learning_outcome_validation or {}).get("diagnostics") or {}
    learning_conf = learning_diag.get("average_learning_outcome_validation_confidence") or 0.0
    learning_cov = (validation_coverage or {}).get("diagnostics", {}).get("learning_outcome_validation_coverage") or 0.0
    learning_impact = _impact_from_signal(learning_conf, learning_cov)
    components.append(
        _build_component(
            "Learning Outcome Validation",
            learning_impact,
            learning_conf,
            [
                "Uses confidence and coverage signals from the learning outcome validation layer.",
                "The assessment remains deterministic and does not depend on title-specific branching.",
            ],
        )
    )

    coverage_diag = (validation_coverage or {}).get("diagnostics") or {}
    coverage_conf = (validation_confidence or {}).get("diagnostics", {}).get("calibrated_overall_validation_confidence") or 0.0
    coverage_value = coverage_diag.get("overall_validation_coverage") or 0.0
    coverage_impact = _impact_from_signal(coverage_conf, coverage_value)
    components.append(
        _build_component(
            "Validation Coverage",
            coverage_impact,
            coverage_conf,
            [
                "Uses overall validation coverage as the main signal for potential impact.",
                "If coverage is sparse, the impact is capped at low or insufficient data.",
            ],
        )
    )

    confidence_diag = (validation_confidence or {}).get("diagnostics") or {}
    overall_confidence = confidence_diag.get("calibrated_overall_validation_confidence") or 0.0
    confidence_impact = _impact_from_signal(overall_confidence, coverage_value)
    components.append(
        _build_component(
            "Validation Confidence",
            confidence_impact,
            overall_confidence,
            [
                "Uses the calibrated confidence score for the validation stack.",
                "Higher confidence indicates more stable impact assessment.",
            ],
        )
    )

    qc_diag = (quality_comparison or {}).get("diagnostics") or {}
    comparison_conf = qc_diag.get("comparison_confidence") or 0.0
    quality_improved = bool(qc_diag.get("quality_improvement_detected"))
    if quality_improved and comparison_conf >= 0.6:
        quality_impact = "high"
    elif comparison_conf >= 0.4:
        quality_impact = "medium"
    elif comparison_conf > 0.0:
        quality_impact = "low"
    else:
        quality_impact = "insufficient_data"
    components.append(
        _build_component(
            "Quality Comparison",
            quality_impact,
            comparison_conf,
            [
                "Uses the quality comparison delta and confidence as the main signal.",
                "A stronger delta with more confidence raises the estimated impact.",
            ],
        )
    )

    rec_diag = (recommendations or {}).get("diagnostics") or {}
    rec_count = rec_diag.get("recommendation_count") or 0
    avg_rec_conf = rec_diag.get("average_recommendation_confidence") or 0.0
    if rec_count >= 3 and avg_rec_conf >= 0.6:
        recommendation_impact = "high"
    elif rec_count >= 1 and avg_rec_conf >= 0.4:
        recommendation_impact = "medium"
    elif rec_count > 0:
        recommendation_impact = "low"
    else:
        recommendation_impact = "insufficient_data"
    components.append(
        _build_component(
            "Recommendation Engine",
            recommendation_impact,
            avg_rec_conf,
            [
                "Uses the number of generated recommendations and their average confidence.",
                "A richer recommendation set suggests stronger shadow-side impact.",
            ],
        )
    )

    promo_diag = (promotion_readiness or {}).get("diagnostics") or {}
    promo_conf = promo_diag.get("overall_readiness_confidence") or 0.0
    promo_status = promo_diag.get("overall_readiness") or "experimental"
    if promo_conf >= 0.7 and promo_status in {"ready", "needs_more_validation"}:
        promotion_impact = "high"
    elif promo_conf >= 0.4:
        promotion_impact = "medium"
    elif promo_conf > 0.0:
        promotion_impact = "low"
    else:
        promotion_impact = "insufficient_data"
    components.append(
        _build_component(
            "Promotion Readiness",
            promotion_impact,
            promo_conf,
            [
                "Uses promotion readiness confidence and the readiness state as the main signal.",
                "A clearer readiness signal suggests more potential impact on deployment decisions.",
            ],
        )
    )

    scores = [_impact_score(component["estimated_impact"]) for component in components]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    avg_confidence = round(sum(component["confidence"] for component in components) / len(components), 2) if components else 0.0
    if average_score >= 2.5:
        overall_impact = "high"
    elif average_score >= 1.5:
        overall_impact = "medium"
    elif average_score >= 0.75:
        overall_impact = "low"
    else:
        overall_impact = "insufficient_data"

    diagnostics = {
        "high_impact_component_count": sum(1 for component in components if component["estimated_impact"] == "high"),
        "medium_impact_component_count": sum(1 for component in components if component["estimated_impact"] == "medium"),
        "low_impact_component_count": sum(1 for component in components if component["estimated_impact"] == "low"),
        "insufficient_data_component_count": sum(1 for component in components if component["estimated_impact"] == "insufficient_data"),
        "overall_estimated_impact": overall_impact,
        "overall_impact_confidence": avg_confidence,
        "source": "runtime_v7_shadow_impact",
    }

    return {
        "shadow_impact": {
            "components": components,
            "overall_estimated_impact": overall_impact,
            "overall_confidence": avg_confidence,
            "diagnostics": diagnostics,
        }
    }
