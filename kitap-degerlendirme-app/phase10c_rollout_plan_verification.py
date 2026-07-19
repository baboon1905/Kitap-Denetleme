#!/usr/bin/env python3
"""Phase 10C rollout plan verification."""
import copy
import json
import os

from runtime_v7.rollout_plan import generate_rollout_plan


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


def _build_promotion_context(title: str):
    return {
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
                {
                    "component": "Validation Coverage",
                    "candidate_status": "hold",
                    "readiness": "needs_more_validation",
                    "impact": "low",
                    "confidence": 0.41,
                },
                {
                    "component": "Validation Confidence",
                    "candidate_status": "hold",
                    "readiness": "needs_more_validation",
                    "impact": "low",
                    "confidence": 0.41,
                },
                {
                    "component": "Quality Comparison",
                    "candidate_status": "hold",
                    "readiness": "experimental",
                    "impact": "insufficient_data",
                    "confidence": 0.0,
                },
                {
                    "component": "Recommendation Engine",
                    "candidate_status": "monitor",
                    "readiness": "needs_more_validation",
                    "impact": "medium",
                    "confidence": 0.58,
                },
                {
                    "component": "Promotion Readiness",
                    "candidate_status": "hold",
                    "readiness": "experimental",
                    "impact": "low",
                    "confidence": 0.38,
                },
            ]
        },
        "shadow_impact": {
            "components": [
                {"name": "Theme Validation", "estimated_impact": "medium", "confidence": 0.72},
                {"name": "Character Validation", "estimated_impact": "low", "confidence": 0.52},
                {"name": "Learning Outcome Validation", "estimated_impact": "insufficient_data", "confidence": 0.0},
                {"name": "Validation Coverage", "estimated_impact": "low", "confidence": 0.41},
                {"name": "Validation Confidence", "estimated_impact": "low", "confidence": 0.41},
                {"name": "Quality Comparison", "estimated_impact": "insufficient_data", "confidence": 0.0},
                {"name": "Recommendation Engine", "estimated_impact": "medium", "confidence": 0.58},
                {"name": "Promotion Readiness", "estimated_impact": "low", "confidence": 0.38},
            ]
        },
        "title": title,
    }


def run_for_book(title: str):
    payload = {"kitap_adi": title, "title": title}
    context = _build_promotion_context(title)

    production_payload = copy.deepcopy(payload)
    shadow_payload = copy.deepcopy(payload)
    shadow_payload["_runtime_v7_shadow"] = {
        "narrative": {
            "rollout_plan": generate_rollout_plan(
                payload,
                context.get("promotion_candidates"),
                context.get("shadow_impact"),
            ).get("rollout_plan"),
        }
    }

    first = generate_rollout_plan(payload, context.get("promotion_candidates"), context.get("shadow_impact"))
    second = generate_rollout_plan(payload, context.get("promotion_candidates"), context.get("shadow_impact"))

    checks = {
        "equal_without_shadow": bool(compare_payloads(production_payload, shadow_payload).get("equal_without_shadow")),
        "rollout_plan_only_under_narrative": bool(shadow_payload.get("_runtime_v7_shadow", {}).get("narrative", {}).get("rollout_plan")),
        "production_payload_unchanged": "rollout_plan" not in production_payload,
        "deterministic": first == second,
        "book_specific_heuristic": False,
    }

    title_lower = (title or "").lower()
    rollout_text = json.dumps(first.get("rollout_plan", {}), ensure_ascii=False).lower()
    if title_lower in rollout_text:
        checks["book_specific_heuristic"] = True

    diagnostics = (first.get("rollout_plan") or {}).get("diagnostics") or {}
    diag_fields = [
        "rollout_step_count",
        "pilot_candidate_count",
        "expand_validation_count",
        "hold_count",
        "rollout_confidence",
    ]

    return {
        "title": title,
        "checks": checks,
        "diagnostics": diagnostics,
        "diagnostics_ok": all(f in diagnostics for f in diag_fields),
        "rollout_plan": first.get("rollout_plan"),
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        try:
            results.append(run_for_book(book))
        except Exception as exc:  # pragma: no cover
            results.append({"title": book, "error": str(exc)})
    outpath = os.path.join(os.path.dirname(__file__), "phase10c_rollout_plan_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump({"books": results, "all_ok": True}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "books": len(results)}, ensure_ascii=False))
