from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _clamp_conf(v: float) -> float:
    try:
        v = float(v)
    except Exception:
        v = 0.0
    if v < 0.0:
        v = 0.0
    if v > 0.99:
        v = 0.99
    return round(v, 2)


def _classify_item(name: str, validation: Dict[str, Any]) -> Tuple[str, float, str]:
    # deterministic, algorithmic rules based on validation confidence and support
    conf = _clamp_conf(validation.get("confidence", 0.0))
    support_flags = [v for k, v in (validation or {}).items() if k != "confidence" and isinstance(v, bool) and v]
    support_count = len(support_flags)

    if conf >= 0.7 and support_count >= 1:
        return "strengthen", conf, "High confidence and supporting signals"
    if 0.45 <= conf < 0.7:
        return "review", conf, "Moderate confidence — human review recommended"
    if conf < 0.45 and support_count == 0:
        return "insufficient_evidence", conf, "Low confidence and no supporting signals"
    return "deprioritize", conf, "Low relative confidence or weak support"


def _make_recommendation(target_type: str, target: str, rec_type: str, reason: str, confidence: float) -> Dict[str, Any]:
    return {
        "target_type": target_type,
        "target": str(target),
        "recommendation_type": rec_type,
        "reason": reason,
        "confidence": round(float(confidence), 2),
    }


def generate_recommendations(
    payload: Dict[str, Any],
    theme_validation: Dict[str, Any],
    character_validation: Dict[str, Any],
    learning_outcome_validation: Dict[str, Any],
) -> Dict[str, Any]:
    # theme_validation, character_validation, learning_outcome_validation are expected
    # to contain lists under keys: 'theme_validation', 'character_validation', 'learning_outcome_validation'
    recommendations: List[Dict[str, Any]] = []

    theme_items = (theme_validation or {}).get("theme_validation") or []
    for item in theme_items:
        name = item.get("theme")
        validation = item.get("validation") or {}
        rec_type, conf, reason = _classify_item(name, validation)
        recommendations.append(_make_recommendation("theme", name or "", rec_type, reason, conf))

    char_items = (character_validation or {}).get("character_validation") or []
    for item in char_items:
        name = item.get("character")
        validation = item.get("validation") or {}
        rec_type, conf, reason = _classify_item(name, validation)
        recommendations.append(_make_recommendation("character", name or "", rec_type, reason, conf))

    lo_items = (learning_outcome_validation or {}).get("learning_outcome_validation") or []
    for item in lo_items:
        name = item.get("learning_outcome")
        validation = item.get("validation") or {}
        rec_type, conf, reason = _classify_item(name, validation)
        recommendations.append(_make_recommendation("learning_outcome", name or "", rec_type, reason, conf))

    # overall recommendations: simple deterministic summary rules
    counts = {"strengthen": 0, "review": 0, "deprioritize": 0, "insufficient_evidence": 0}
    for r in recommendations:
        rt = r.get("recommendation_type")
        if rt in counts:
            counts[rt] += 1

    overall_recommendations: List[Dict[str, Any]] = []
    total = max(1, len(recommendations))
    if counts["strengthen"] / total >= 0.5:
        overall_recommendations.append(_make_recommendation("overall", "narrative", "strengthen", "Majority of validated items are strong", round(counts["strengthen"]/total, 2)))
    elif counts["insufficient_evidence"] / total >= 0.5:
        overall_recommendations.append(_make_recommendation("overall", "narrative", "insufficient_evidence", "Majority of items lack evidence", round(counts["insufficient_evidence"]/total, 2)))
    else:
        # default: suggest review if mixed signals
        overall_recommendations.append(_make_recommendation("overall", "narrative", "review", "Mixed or moderate signals — human review recommended", round((counts["review"]/total), 2)))

    # assemble structured output grouped by target type (preserve deterministic order)
    theme_recs = [r for r in recommendations if r.get("target_type") == "theme"]
    char_recs = [r for r in recommendations if r.get("target_type") == "character"]
    lo_recs = [r for r in recommendations if r.get("target_type") == "learning_outcome"]

    grouped = {
        "recommendations": {
            "theme_recommendations": theme_recs,
            "character_recommendations": char_recs,
            "learning_outcome_recommendations": lo_recs,
            "overall_recommendations": overall_recommendations,
        }
    }

    # diagnostics counts and average confidence
    confs = [float(r.get("confidence") or 0.0) for r in recommendations]
    avg_conf = round(sum(confs) / len(confs), 2) if confs else 0.0
    diag = {
        "recommendation_count": len(recommendations),
        "review_recommendation_count": counts.get("review", 0),
        "strengthen_recommendation_count": counts.get("strengthen", 0),
        "deprioritize_recommendation_count": counts.get("deprioritize", 0),
        "insufficient_evidence_recommendation_count": counts.get("insufficient_evidence", 0),
        "average_recommendation_confidence": avg_conf,
        "source": "runtime_v7_recommendation_engine",
    }

    grouped["diagnostics"] = diag
    return grouped
