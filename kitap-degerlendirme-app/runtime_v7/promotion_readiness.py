from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _clamp(v: float) -> float:
    try:
        v = float(v)
    except Exception:
        v = 0.0
    if v < 0.0:
        v = 0.0
    if v > 0.99:
        v = 0.99
    return round(v, 2)


def _component_readiness(name: str, confidence: float, coverage: float = 1.0) -> Tuple[str, float, List[str]]:
    conf = _clamp(confidence)
    reasons: List[str] = []
    if conf >= 0.7 and coverage >= 1.0:
        readiness = "ready"
        reasons.append("High confidence and full coverage")
    elif conf >= 0.45 and coverage >= 0.5:
        readiness = "needs_more_validation"
        reasons.append("Moderate confidence or partial coverage — human validation suggested")
    else:
        readiness = "experimental"
        reasons.append("Low confidence or insufficient coverage — experimental only")
    return readiness, conf, reasons


def generate_promotion_readiness(
    payload: Dict[str, Any],
    theme_validation: Dict[str, Any],
    character_validation: Dict[str, Any],
    learning_outcome_validation: Dict[str, Any],
    validation_coverage: Dict[str, Any],
    validation_confidence: Dict[str, Any],
    quality_comparison: Dict[str, Any],
    recommendations: Dict[str, Any],
) -> Dict[str, Any]:
    components: List[Dict[str, Any]] = []

    # theme_validation
    theme_conf = (validation_confidence or {}).get("calibrated_theme_validation_confidence") or (theme_validation or {}).get("diagnostics", {}).get("average_theme_validation_confidence") or 0.0
    theme_cov = (validation_coverage or {}).get("diagnostics", {}).get("theme_validation_coverage") or 1.0
    r, c, reasons = _component_readiness("theme_validation", theme_conf, theme_cov)
    components.append({"name": "theme_validation", "readiness": r, "confidence": c, "reasons": reasons})

    # character_validation
    char_conf = (validation_confidence or {}).get("calibrated_character_validation_confidence") or (character_validation or {}).get("diagnostics", {}).get("average_character_validation_confidence") or 0.0
    char_cov = (validation_coverage or {}).get("diagnostics", {}).get("character_validation_coverage") or 1.0
    r, c, reasons = _component_readiness("character_validation", char_conf, char_cov)
    components.append({"name": "character_validation", "readiness": r, "confidence": c, "reasons": reasons})

    # learning_outcome_validation
    lo_conf = (validation_confidence or {}).get("calibrated_learning_outcome_validation_confidence") or (learning_outcome_validation or {}).get("diagnostics", {}).get("average_learning_outcome_validation_confidence") or 0.0
    lo_cov = (validation_coverage or {}).get("diagnostics", {}).get("learning_outcome_validation_coverage") or 0.0
    r, c, reasons = _component_readiness("learning_outcome_validation", lo_conf, lo_cov)
    components.append({"name": "learning_outcome_validation", "readiness": r, "confidence": c, "reasons": reasons})

    # validation_coverage (overall)
    overall_cov = (validation_coverage or {}).get("diagnostics", {}).get("overall_validation_coverage") or 0.0
    overall_conf_from_cov = (validation_confidence or {}).get("diagnostics", {}).get("calibrated_overall_validation_confidence") or 0.0
    r, c, reasons = _component_readiness("validation_coverage", overall_conf_from_cov, overall_cov)
    components.append({"name": "validation_coverage", "readiness": r, "confidence": c, "reasons": reasons})

    # validation_confidence
    overall_conf = (validation_confidence or {}).get("diagnostics", {}).get("calibrated_overall_validation_confidence") or 0.0
    r, c, reasons = _component_readiness("validation_confidence", overall_conf, overall_cov)
    components.append({"name": "validation_confidence", "readiness": r, "confidence": c, "reasons": reasons})

    # quality_comparison
    qc_diag = (quality_comparison or {}).get("diagnostics") or {}
    comparison_conf = qc_diag.get("comparison_confidence") or 0.0
    quality_improved = bool(qc_diag.get("quality_improvement_detected"))
    # deterministic mapping
    if quality_improved and comparison_conf >= 0.6:
        qr = "ready"
        qreasons = ["Quality improved with high confidence"]
    elif comparison_conf >= 0.4:
        qr = "needs_more_validation"
        qreasons = ["Quality change detected but needs human validation"]
    else:
        qr = "experimental"
        qreasons = ["No reliable quality comparison signal"]
    components.append({"name": "quality_comparison", "readiness": qr, "confidence": _clamp(comparison_conf), "reasons": qreasons})

    # recommendations (are there outstanding suggestions?)
    rec_diag = (recommendations or {}).get("diagnostics") or {}
    rec_count = rec_diag.get("recommendation_count") or 0
    rec_avg = rec_diag.get("average_recommendation_confidence") or 0.0
    if rec_count == 0:
        rr = "ready"
        rreasons = ["No recommended changes"]
    elif rec_avg >= 0.6:
        rr = "needs_more_validation"
        rreasons = ["High-confidence recommendations require review before promotion"]
    else:
        rr = "experimental"
        rreasons = ["Low-confidence recommendations — treat as experimental"]
    components.append({"name": "recommendations", "readiness": rr, "confidence": _clamp(rec_avg), "reasons": rreasons})

    # aggregate overall readiness by majority vote of component readiness
    counts = {"ready": 0, "needs_more_validation": 0, "experimental": 0}
    confs: List[float] = []
    for comp in components:
        counts[comp["readiness"]] += 1
        confs.append(float(comp.get("confidence") or 0.0))

    overall_readiness = max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
    overall_confidence = round(sum(confs) / len(confs), 2) if confs else 0.0

    diagnostics = {
        "ready_component_count": counts.get("ready", 0),
        "experimental_component_count": counts.get("experimental", 0),
        "needs_validation_component_count": counts.get("needs_more_validation", 0),
        "overall_readiness": overall_readiness,
        "overall_readiness_confidence": overall_confidence,
        "source": "runtime_v7_promotion_readiness",
    }

    return {
        "promotion_readiness": {"components": components, "overall_readiness": overall_readiness, "overall_confidence": overall_confidence},
        "diagnostics": diagnostics,
    }
