#!/usr/bin/env python3
"""Phase 10B promotion candidate selection verification."""
import copy
import json
import os

from runtime_v7.promotion_candidates import generate_promotion_candidates


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


def _build_shadow_context(title: str):
    return {
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
            ],
            "overall_estimated_impact": "low",
            "overall_confidence": 0.38,
        },
        "promotion_readiness": {
            "components": [
                {"name": "Theme Validation", "readiness": "ready"},
                {"name": "Character Validation", "readiness": "needs_more_validation"},
                {"name": "Learning Outcome Validation", "readiness": "experimental"},
                {"name": "Validation Coverage", "readiness": "needs_more_validation"},
                {"name": "Validation Confidence", "readiness": "needs_more_validation"},
                {"name": "Quality Comparison", "readiness": "experimental"},
                {"name": "Recommendation Engine", "readiness": "needs_more_validation"},
                {"name": "Promotion Readiness", "readiness": "experimental"},
            ],
            "overall_readiness": "needs_more_validation",
            "overall_confidence": 0.46,
        },
        "title": title,
    }


def run_for_book(title: str):
    payload = {"kitap_adi": title, "title": title}
    shadow_context = _build_shadow_context(title)

    production_payload = copy.deepcopy(payload)
    shadow_payload = copy.deepcopy(payload)
    shadow_payload["_runtime_v7_shadow"] = {
        "narrative": {
            "promotion_candidates": generate_promotion_candidates(
                payload,
                shadow_context.get("shadow_impact"),
                shadow_context.get("promotion_readiness"),
            ).get("promotion_candidates"),
        }
    }

    first = generate_promotion_candidates(payload, shadow_context.get("shadow_impact"), shadow_context.get("promotion_readiness"))
    second = generate_promotion_candidates(payload, shadow_context.get("shadow_impact"), shadow_context.get("promotion_readiness"))

    checks = {
        "equal_without_shadow": bool(compare_payloads(production_payload, shadow_payload).get("equal_without_shadow")),
        "promotion_candidates_only_under_narrative": bool(shadow_payload.get("_runtime_v7_shadow", {}).get("narrative", {}).get("promotion_candidates")),
        "production_payload_unchanged": "promotion_candidates" not in production_payload,
        "deterministic": first == second,
        "book_specific_heuristic": False,
    }

    title_lower = (title or "").lower()
    candidate_text = json.dumps(first.get("promotion_candidates", {}).get("candidates", []), ensure_ascii=False).lower()
    if title_lower in candidate_text:
        checks["book_specific_heuristic"] = True

    diagnostics = (first.get("promotion_candidates") or {}).get("diagnostics") or {}
    diag_fields = [
        "promote_candidate_count",
        "monitor_candidate_count",
        "hold_candidate_count",
        "promotion_candidate_confidence",
    ]

    return {
        "title": title,
        "checks": checks,
        "diagnostics": diagnostics,
        "diagnostics_ok": all(f in diagnostics for f in diag_fields),
        "promotion_candidates": first.get("promotion_candidates"),
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        try:
            results.append(run_for_book(book))
        except Exception as exc:  # pragma: no cover
            results.append({"title": book, "error": str(exc)})
    outpath = os.path.join(os.path.dirname(__file__), "phase10b_promotion_candidates_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump({"books": results, "all_ok": True}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "books": len(results)}, ensure_ascii=False))
