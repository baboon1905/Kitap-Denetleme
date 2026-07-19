#!/usr/bin/env python3
"""
Local Phase9A Recommendation Engine Verification (lightweight)
Uses an existing prepared payload sample to exercise the adapter and recommendation engine
without reprocessing PDFs.
"""
import copy
import json
import os
from typing import Any

from runtime_v7.adapter import build_v7_shadow_payload

BASE_PAYLOAD_PATH = os.path.join(os.path.dirname(__file__), "debug_stage3_final_pdf_payload.json")
BOOKS = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
REQUIRED_REC_TYPES = {"strengthen", "review", "deprioritize", "insufficient_evidence"}


def _equal_without_shadow(original: dict, with_shadow_attached: dict) -> bool:
    a = copy.deepcopy(original)
    b = copy.deepcopy(with_shadow_attached)
    b.pop("_runtime_v7_shadow", None)
    return a == b


def run():
    with open(BASE_PAYLOAD_PATH, 'r', encoding='utf-8') as fh:
        base = json.load(fh)

    results = []
    all_ok = True

    for title in BOOKS:
        payload = copy.deepcopy(base)
        # set title/book fields
        payload["kitap_adi"] = title
        payload["baslik"] = title
        payload["title"] = title

        # ensure no mutation from build function
        original_copy = copy.deepcopy(payload)

        # turn on narrative graph flag
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        os.environ['V7_SHADOW_MODE'] = 'true'

        shadow = build_v7_shadow_payload(payload)

        # production payload unchanged when attaching shadow
        prod = copy.deepcopy(payload)
        prod["_runtime_v7_shadow"] = shadow
        prod_unchanged = _equal_without_shadow(original_copy, prod)

        narrative = shadow.get("narrative") if isinstance(shadow, dict) else None
        recommendations = (narrative or {}).get("recommendations") if isinstance(narrative, dict) else None
        diagnostics = (narrative or {}).get("diagnostics") if isinstance(narrative, dict) else {}

        rec_checks = {
            "recommendations_in_shadow_only": True,
            "production_payload_unchanged": prod_unchanged,
            "recommendation_diagnostics_valid": all(k in diagnostics for k in (
                "recommendation_count",
                "review_recommendation_count",
                "strengthen_recommendation_count",
                "deprioritize_recommendation_count",
                "insufficient_evidence_recommendation_count",
                "average_recommendation_confidence",
            )),
            "recommendation_types_valid": True,
            "deterministic": False,
            "book_specific_heuristic": False,
        }

        # Ensure root has no 'recommendations' key
        if "recommendations" in original_copy:
            rec_checks["recommendations_in_shadow_only"] = False

        # Validate recommendation types and presence
        all_recs = []
        if isinstance(recommendations, dict):
            for k in ("theme_recommendations", "character_recommendations", "learning_outcome_recommendations", "overall_recommendations"):
                arr = recommendations.get(k) or []
                if isinstance(arr, list):
                    all_recs.extend(arr)
        else:
            all_recs = []

        for r in all_recs:
            if r.get("recommendation_type") not in REQUIRED_REC_TYPES:
                rec_checks["recommendation_types_valid"] = False

        # Determinism: run twice
        s1 = build_v7_shadow_payload(payload)
        s2 = build_v7_shadow_payload(payload)
        rec_checks["deterministic"] = s1 == s2

        # Book-specific heuristic detection (simple): title appears in recommendation reason or target
        lower_title = title.lower()
        text = json.dumps(recommendations or {}, ensure_ascii=False).lower()
        if lower_title in text:
            rec_checks["book_specific_heuristic"] = True

        ok = rec_checks["production_payload_unchanged"] and rec_checks["recommendation_diagnostics_valid"] and rec_checks["recommendation_types_valid"] and rec_checks["deterministic"] and (not rec_checks["book_specific_heuristic"])
        if not ok:
            all_ok = False

        results.append({"title": title, "recommendation_checks": rec_checks, "recommendations_summary": {"count": len(all_recs)}})

    out = {"books": results, "all_ok": all_ok}
    outpath = os.path.join(os.path.dirname(__file__), "phase9a_recommendation_engine_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "all_ok": all_ok}, ensure_ascii=False))


if __name__ == '__main__':
    run()
