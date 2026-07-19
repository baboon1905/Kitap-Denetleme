from __future__ import annotations

from typing import Any, Dict, List, Tuple


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


def _count_items(container: Any, key: str) -> int:
    """Count items in a container (dict or list) by key."""
    if isinstance(container, dict):
        items = container.get(key)
        if isinstance(items, list):
            return len(items)
        return 1 if items else 0
    return 0


def _assess_component_status(component: Dict[str, Any]) -> Tuple[str, str, float]:
    """
    Assess a component's status and return (severity, message, confidence).
    Returns: ("info" | "warning" | "critical", message, confidence)
    """
    name = component.get("name", "unknown")
    readiness = component.get("readiness", "experimental")
    confidence = _clamp_conf(component.get("confidence", 0.0))
    impact = component.get("impact", "insufficient_data")
    reasons = component.get("reasons", [])

    severity = "info"
    message = f"{name}: {readiness} (confidence: {confidence})"

    # Deterministic mapping: high confidence, ready state -> info
    if readiness == "ready" and confidence >= 0.7:
        severity = "info"
        message = f"{name}: ready for production (confidence: {confidence})"
    # moderate confidence, needs validation -> warning
    elif readiness == "needs_more_validation" and confidence >= 0.5:
        severity = "warning"
        message = f"{name}: needs more validation (confidence: {confidence})"
    # low confidence or experimental -> critical
    elif readiness == "experimental" or confidence < 0.3:
        severity = "critical"
        message = f"{name}: experimental phase, more data needed (confidence: {confidence})"

    # Impact assessment can elevate severity
    if impact == "high" and severity == "info":
        severity = "warning"
        message = f"{name}: high-impact component with moderate confidence (confidence: {confidence})"

    return severity, message, confidence


def _generate_audit_findings(
    payload: Dict[str, Any],
    promotion_readiness: Dict[str, Any],
    shadow_impact: Dict[str, Any],
    promotion_candidates: Dict[str, Any],
    recommendations: Dict[str, Any],
    rollout_plan: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate audit findings from shadow components."""
    findings: List[Dict[str, Any]] = []

    # Audit promotion readiness components
    readiness_components = (promotion_readiness or {}).get("components") or []
    for component in readiness_components:
        if not isinstance(component, dict):
            continue
        severity, message, confidence = _assess_component_status(component)
        findings.append({
            "category": "promotion_readiness",
            "severity": severity,
            "message": message,
            "confidence": confidence,
        })

    # Audit shadow impact components
    impact_components = (shadow_impact or {}).get("components") or []
    for component in impact_components:
        if not isinstance(component, dict):
            continue
        name = component.get("name", "unknown")
        impact = component.get("estimated_impact", "insufficient_data")
        confidence = _clamp_conf(component.get("confidence", 0.0))

        severity = "info"
        message = f"{name}: {impact} impact"

        if impact == "high" and confidence >= 0.7:
            severity = "info"
            message = f"{name}: high-impact component confirmed (confidence: {confidence})"
        elif impact in {"medium", "low"} and confidence >= 0.5:
            severity = "warning"
            message = f"{name}: moderate-impact with medium confidence (confidence: {confidence})"
        elif impact == "insufficient_data" or confidence < 0.3:
            severity = "critical"
            message = f"{name}: insufficient data or low confidence (confidence: {confidence})"

        findings.append({
            "category": "shadow_impact",
            "severity": severity,
            "message": message,
            "confidence": confidence,
        })

    # Audit recommendations
    recommendations_dict = (recommendations or {}).get("recommendations") or {}
    rec_theme = (recommendations_dict.get("theme_recommendations") or [])
    rec_char = (recommendations_dict.get("character_recommendations") or [])
    rec_lo = (recommendations_dict.get("learning_outcome_recommendations") or [])

    theme_strengthen = len([r for r in rec_theme if (r or {}).get("recommendation_type") == "strengthen"])
    theme_review = len([r for r in rec_theme if (r or {}).get("recommendation_type") == "review"])
    theme_insufficient = len([r for r in rec_theme if (r or {}).get("recommendation_type") == "insufficient_evidence"])

    if theme_strengthen >= theme_review and theme_strengthen > 0:
        findings.append({
            "category": "recommendations",
            "severity": "info",
            "message": f"Theme validation: {theme_strengthen} items ready to strengthen",
            "confidence": round(theme_strengthen / max(1, len(rec_theme)), 2),
        })
    elif theme_review > 0:
        findings.append({
            "category": "recommendations",
            "severity": "warning",
            "message": f"Theme validation: {theme_review} items need human review",
            "confidence": round(theme_review / max(1, len(rec_theme)), 2),
        })
    if theme_insufficient > 0:
        findings.append({
            "category": "recommendations",
            "severity": "critical",
            "message": f"Theme validation: {theme_insufficient} items have insufficient evidence",
            "confidence": round(theme_insufficient / max(1, len(rec_theme)), 2),
        })

    char_strengthen = len([r for r in rec_char if (r or {}).get("recommendation_type") == "strengthen"])
    char_review = len([r for r in rec_char if (r or {}).get("recommendation_type") == "review"])

    if char_strengthen >= char_review and char_strengthen > 0:
        findings.append({
            "category": "recommendations",
            "severity": "info",
            "message": f"Character validation: {char_strengthen} items ready to strengthen",
            "confidence": round(char_strengthen / max(1, len(rec_char)), 2),
        })
    elif char_review > 0:
        findings.append({
            "category": "recommendations",
            "severity": "warning",
            "message": f"Character validation: {char_review} items need review",
            "confidence": round(char_review / max(1, len(rec_char)), 2),
        })

    lo_strengthen = len([r for r in rec_lo if (r or {}).get("recommendation_type") == "strengthen"])
    lo_review = len([r for r in rec_lo if (r or {}).get("recommendation_type") == "review"])

    if lo_strengthen >= lo_review and lo_strengthen > 0:
        findings.append({
            "category": "recommendations",
            "severity": "info",
            "message": f"Learning outcome validation: {lo_strengthen} items ready to strengthen",
            "confidence": round(lo_strengthen / max(1, len(rec_lo)), 2),
        })
    elif lo_review > 0:
        findings.append({
            "category": "recommendations",
            "severity": "warning",
            "message": f"Learning outcome validation: {lo_review} items need review",
            "confidence": round(lo_review / max(1, len(rec_lo)), 2),
        })

    # Audit rollout plan
    rollout_steps = (rollout_plan or {}).get("steps") or []
    pilot_count = len([s for s in rollout_steps if (s or {}).get("action") == "pilot_candidate"])
    expand_count = len([s for s in rollout_steps if (s or {}).get("action") == "expand_validation"])
    hold_count = len([s for s in rollout_steps if (s or {}).get("action") == "hold"])

    if pilot_count > 0:
        findings.append({
            "category": "rollout_plan",
            "severity": "info",
            "message": f"Rollout plan: {pilot_count} components ready for pilot",
            "confidence": 0.75,
        })
    if expand_count > 0:
        findings.append({
            "category": "rollout_plan",
            "severity": "warning",
            "message": f"Rollout plan: {expand_count} components need validation expansion",
            "confidence": 0.65,
        })
    if hold_count >= max(pilot_count, expand_count) and hold_count > 0:
        findings.append({
            "category": "rollout_plan",
            "severity": "critical",
            "message": f"Rollout plan: {hold_count} components on hold pending improvements",
            "confidence": round(hold_count / max(1, len(rollout_steps)), 2),
        })

    # Overall recommendations sentiment
    overall_recs = (recommendations_dict.get("overall_recommendations") or [])
    for rec in overall_recs:
        if not isinstance(rec, dict):
            continue
        rec_type = rec.get("recommendation_type", "unknown")
        if rec_type == "strengthen":
            findings.append({
                "category": "overall_sentiment",
                "severity": "info",
                "message": "Overall narrative readiness: Strong signals detected",
                "confidence": _clamp_conf(rec.get("confidence", 0.0)),
            })
        elif rec_type == "review":
            findings.append({
                "category": "overall_sentiment",
                "severity": "warning",
                "message": "Overall narrative readiness: Mixed signals - human review recommended",
                "confidence": _clamp_conf(rec.get("confidence", 0.0)),
            })
        elif rec_type == "insufficient_evidence":
            findings.append({
                "category": "overall_sentiment",
                "severity": "critical",
                "message": "Overall narrative readiness: Insufficient evidence - more validation needed",
                "confidence": _clamp_conf(rec.get("confidence", 0.0)),
            })

    return findings


def generate_shadow_audit(
    payload: Dict[str, Any],
    promotion_readiness: Dict[str, Any],
    shadow_impact: Dict[str, Any],
    promotion_candidates: Dict[str, Any],
    recommendations: Dict[str, Any],
    rollout_plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate shadow audit report summarizing all V7 shadow components.
    
    Args:
        payload: Original payload (used for context only)
        promotion_readiness: Promotion readiness assessment
        shadow_impact: Shadow impact assessment
        promotion_candidates: Promotion candidates
        recommendations: Recommendations from recommendation engine
        rollout_plan: Rollout plan
    
    Returns:
        Dict with shadow_audit structure containing summary and findings
    """
    # Count components
    readiness_components = (promotion_readiness or {}).get("components") or []
    impact_components = (shadow_impact or {}).get("components") or []
    candidates = (promotion_candidates or {}).get("candidates") or []
    rollout_steps = (rollout_plan or {}).get("steps") or []

    component_count = len(readiness_components) + len(impact_components)
    ready_count = len([c for c in readiness_components if (c or {}).get("readiness") == "ready"])
    high_impact_count = len([c for c in impact_components if (c or {}).get("estimated_impact") == "high"])

    recommendations_dict = (recommendations or {}).get("recommendations") or {}
    rec_theme = (recommendations_dict.get("theme_recommendations") or [])
    rec_char = (recommendations_dict.get("character_recommendations") or [])
    rec_lo = (recommendations_dict.get("learning_outcome_recommendations") or [])
    recommendation_count = len(rec_theme) + len(rec_char) + len(rec_lo)

    rollout_step_count = len(rollout_steps)

    # Generate findings
    findings = _generate_audit_findings(
        payload,
        promotion_readiness,
        shadow_impact,
        promotion_candidates,
        recommendations,
        rollout_plan,
    )

    # Count findings by severity
    info_count = len([f for f in findings if f.get("severity") == "info"])
    warning_count = len([f for f in findings if f.get("severity") == "warning"])
    critical_count = len([f for f in findings if f.get("severity") == "critical"])

    # Calculate aggregate confidence
    avg_confidence = 0.0
    if findings:
        avg_confidence = round(sum(f.get("confidence", 0.0) for f in findings) / len(findings), 2)

    summary = {
        "component_count": component_count,
        "ready_component_count": ready_count,
        "high_impact_component_count": high_impact_count,
        "recommendation_count": recommendation_count,
        "rollout_step_count": rollout_step_count,
    }

    diagnostics = {
        "audit_finding_count": len(findings),
        "audit_info_count": info_count,
        "audit_warning_count": warning_count,
        "audit_critical_count": critical_count,
        "audit_confidence": avg_confidence,
        "source": "runtime_v7_shadow_audit",
    }

    return {
        "shadow_audit": {
            "summary": summary,
            "findings": findings,
            "diagnostics": diagnostics,
        }
    }
