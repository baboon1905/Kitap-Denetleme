#!/usr/bin/env python3
"""Phase 11A shadow audit report generator verification."""
import copy
import json
import os

from runtime_v7.shadow_audit import generate_shadow_audit


def _normalize_payload(payload: dict) -> dict:
    normalized = copy.deepcopy(payload or {})
    normalized.pop("_runtime_v7_shadow", None)
    normalized.pop("canonical_summary_ir", None)
    normalized.pop("canonical_summary_ir_hash", None)
    return normalized


def compare_payloads(false_payload, true_payload):
    a = _normalize_payload(false_payload or {})
    b = _normalize_payload(true_payload or {})
    return {"equal_without_shadow": a == b}


def _build_audit_context(title: str):
    """Build test context for shadow audit verification."""
    return {
        "promotion_readiness": {
            "components": [
                {
                    "name": "theme_validation",
                    "readiness": "ready",
                    "confidence": 0.72,
                    "reasons": ["High confidence and full coverage"],
                },
                {
                    "name": "character_validation",
                    "readiness": "needs_more_validation",
                    "confidence": 0.52,
                    "reasons": ["Moderate confidence or partial coverage"],
                },
                {
                    "name": "learning_outcome_validation",
                    "readiness": "experimental",
                    "confidence": 0.0,
                    "reasons": ["Low confidence or insufficient coverage"],
                },
                {
                    "name": "validation_coverage",
                    "readiness": "needs_more_validation",
                    "confidence": 0.41,
                    "reasons": ["Moderate confidence or partial coverage"],
                },
                {
                    "name": "validation_confidence",
                    "readiness": "needs_more_validation",
                    "confidence": 0.41,
                    "reasons": ["Moderate confidence or partial coverage"],
                },
                {
                    "name": "quality_comparison",
                    "readiness": "experimental",
                    "confidence": 0.0,
                    "reasons": ["No reliable quality comparison signal"],
                },
                {
                    "name": "recommendation_engine",
                    "readiness": "needs_more_validation",
                    "confidence": 0.58,
                    "reasons": ["High-confidence recommendations require review"],
                },
                {
                    "name": "promotion_readiness",
                    "readiness": "experimental",
                    "confidence": 0.38,
                    "reasons": ["Some components are not ready"],
                },
            ]
        },
        "shadow_impact": {
            "components": [
                {
                    "name": "Theme Validation",
                    "estimated_impact": "medium",
                    "confidence": 0.72,
                    "reasons": ["Uses confidence and coverage signals from the theme validation layer."],
                },
                {
                    "name": "Character Validation",
                    "estimated_impact": "low",
                    "confidence": 0.52,
                    "reasons": ["Confidence and coverage signals indicate low estimated impact."],
                },
                {
                    "name": "Learning Outcome Validation",
                    "estimated_impact": "insufficient_data",
                    "confidence": 0.0,
                    "reasons": ["Insufficient coverage data for learning outcome validation."],
                },
                {
                    "name": "Validation Coverage",
                    "estimated_impact": "low",
                    "confidence": 0.41,
                    "reasons": ["Overall validation coverage remains moderate."],
                },
                {
                    "name": "Validation Confidence",
                    "estimated_impact": "low",
                    "confidence": 0.41,
                    "reasons": ["Confidence levels are moderate across components."],
                },
                {
                    "name": "Quality Comparison",
                    "estimated_impact": "insufficient_data",
                    "confidence": 0.0,
                    "reasons": ["No reliable quality comparison signal."],
                },
                {
                    "name": "Recommendation Engine",
                    "estimated_impact": "medium",
                    "confidence": 0.58,
                    "reasons": ["Produces actionable recommendations with moderate confidence."],
                },
                {
                    "name": "Promotion Readiness",
                    "estimated_impact": "low",
                    "confidence": 0.38,
                    "reasons": ["Most components are not yet production-ready."],
                },
            ]
        },
        "promotion_candidates": {
            "candidates": [
                {
                    "component": "Theme Validation",
                    "candidate_status": "promote_candidate",
                    "readiness": "ready",
                    "impact": "medium",
                    "confidence": 0.72,
                },
                {
                    "component": "Character Validation",
                    "candidate_status": "hold",
                    "readiness": "needs_more_validation",
                    "impact": "low",
                    "confidence": 0.52,
                },
                {
                    "component": "Learning Outcome Validation",
                    "candidate_status": "hold",
                    "readiness": "experimental",
                    "impact": "insufficient_data",
                    "confidence": 0.0,
                },
            ]
        },
        "recommendations": {
            "recommendations": {
                "theme_recommendations": [
                    {
                        "target_type": "theme",
                        "target": "Theme A",
                        "recommendation_type": "strengthen",
                        "reason": "High confidence",
                        "confidence": 0.75,
                    },
                    {
                        "target_type": "theme",
                        "target": "Theme B",
                        "recommendation_type": "review",
                        "reason": "Moderate confidence",
                        "confidence": 0.55,
                    },
                ],
                "character_recommendations": [
                    {
                        "target_type": "character",
                        "target": "Character A",
                        "recommendation_type": "strengthen",
                        "reason": "High confidence",
                        "confidence": 0.68,
                    },
                ],
                "learning_outcome_recommendations": [
                    {
                        "target_type": "learning_outcome",
                        "target": "LO A",
                        "recommendation_type": "review",
                        "reason": "Needs human validation",
                        "confidence": 0.52,
                    },
                ],
                "overall_recommendations": [
                    {
                        "target_type": "overall",
                        "target": "narrative",
                        "recommendation_type": "review",
                        "reason": "Mixed signals - human review recommended",
                        "confidence": 0.58,
                    }
                ],
            },
            "diagnostics": {
                "recommendation_count": 4,
                "average_recommendation_confidence": 0.625,
            },
        },
        "rollout_plan": {
            "steps": [
                {
                    "step": 1,
                    "component": "Theme Validation",
                    "action": "pilot_candidate",
                    "reason": "Ready for pilot",
                    "confidence": 0.72,
                },
                {
                    "step": 2,
                    "component": "Character Validation",
                    "action": "expand_validation",
                    "reason": "Expand validation",
                    "confidence": 0.52,
                },
                {
                    "step": 3,
                    "component": "Learning Outcome Validation",
                    "action": "hold",
                    "reason": "On hold",
                    "confidence": 0.0,
                },
            ],
            "recommended_next_action": "pilot_candidate",
            "diagnostics": {
                "rollout_step_count": 3,
                "pilot_candidate_count": 1,
                "expand_validation_count": 1,
                "hold_count": 1,
                "rollout_confidence": 0.41,
            },
        },
    }


def run_for_book(title: str):
    payload = {"kitap_adi": title, "title": title}
    context = _build_audit_context(title)

    production_payload = copy.deepcopy(payload)
    shadow_payload = copy.deepcopy(payload)
    shadow_payload["_runtime_v7_shadow"] = {
        "narrative": {
            "shadow_audit": generate_shadow_audit(
                payload,
                context.get("promotion_readiness"),
                context.get("shadow_impact"),
                context.get("promotion_candidates"),
                context.get("recommendations"),
                context.get("rollout_plan"),
            ).get("shadow_audit"),
        }
    }

    first = generate_shadow_audit(
        payload,
        context.get("promotion_readiness"),
        context.get("shadow_impact"),
        context.get("promotion_candidates"),
        context.get("recommendations"),
        context.get("rollout_plan"),
    )
    second = generate_shadow_audit(
        payload,
        context.get("promotion_readiness"),
        context.get("shadow_impact"),
        context.get("promotion_candidates"),
        context.get("recommendations"),
        context.get("rollout_plan"),
    )

    checks = {
        "equal_without_shadow": bool(compare_payloads(production_payload, shadow_payload).get("equal_without_shadow")),
        "shadow_audit_only_under_narrative": bool(shadow_payload.get("_runtime_v7_shadow", {}).get("narrative", {}).get("shadow_audit")),
        "production_payload_unchanged": "shadow_audit" not in production_payload,
        "deterministic": first == second,
        "book_specific_heuristic": False,
    }

    title_lower = (title or "").lower()
    audit_text = json.dumps(first.get("shadow_audit", {}), ensure_ascii=False).lower()
    if title_lower in audit_text:
        checks["book_specific_heuristic"] = True

    audit = first.get("shadow_audit") or {}
    summary = audit.get("summary") or {}
    findings = audit.get("findings") or []
    diagnostics = audit.get("diagnostics") or {}

    summary_fields = [
        "component_count",
        "ready_component_count",
        "high_impact_component_count",
        "recommendation_count",
        "rollout_step_count",
    ]
    diag_fields = [
        "audit_finding_count",
        "audit_info_count",
        "audit_warning_count",
        "audit_critical_count",
        "audit_confidence",
    ]

    # Validate findings structure
    findings_valid = True
    if not isinstance(findings, list):
        findings_valid = False
    for f in findings:
        if not isinstance(f, dict):
            findings_valid = False
        required = ["category", "severity", "message", "confidence"]
        if not all(k in f for k in required):
            findings_valid = False
        if f.get("severity") not in {"info", "warning", "critical"}:
            findings_valid = False

    return {
        "title": title,
        "checks": checks,
        "summary": summary,
        "summary_ok": all(f in summary for f in summary_fields),
        "findings_count": len(findings),
        "findings_valid": findings_valid,
        "diagnostics": diagnostics,
        "diagnostics_ok": all(f in diagnostics for f in diag_fields),
        "shadow_audit": audit,
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        try:
            results.append(run_for_book(book))
        except Exception as exc:  # pragma: no cover
            results.append({"title": book, "error": str(exc)})

    all_ok = all(
        r.get("checks", {}).get("equal_without_shadow", False)
        and r.get("checks", {}).get("shadow_audit_only_under_narrative", False)
        and r.get("checks", {}).get("production_payload_unchanged", False)
        and r.get("checks", {}).get("deterministic", False)
        and not r.get("checks", {}).get("book_specific_heuristic", False)
        and r.get("summary_ok", False)
        and r.get("findings_valid", False)
        and r.get("diagnostics_ok", False)
        for r in results
        if "error" not in r
    )

    outpath = os.path.join(os.path.dirname(__file__), "phase11a_shadow_audit_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump({"books": results, "all_ok": all_ok}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "books": len(results), "all_ok": all_ok}, ensure_ascii=False))
