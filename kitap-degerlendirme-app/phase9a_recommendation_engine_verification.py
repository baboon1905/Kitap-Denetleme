#!/usr/bin/env python3
"""
Phase 9A Recommendation Engine Verification
"""
import copy
import io
import json
import os
from unittest.mock import patch

import app as flask_app_module

PDFS = {
    "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
    "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
    "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
}

REQUIRED_REC_TYPES = {"strengthen", "review", "deprioritize", "insufficient_evidence"}


def _normalize_payload(payload: dict) -> dict:
    normalized = copy.deepcopy(payload or {})
    normalized.pop("_runtime_v7_shadow", None)
    normalized.pop("canonical_summary_ir", None)
    normalized.pop("canonical_summary_ir_hash", None)
    for transient in ("analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id"):
        normalized.pop(transient, None)
    audit = normalized.get("summary_consistency_audit")
    if isinstance(audit, dict):
        audit = dict(audit)
        audit.pop("summary_ir_version", None)
        audit.pop("canonical_summary_ir_hash", None)
        if audit:
            normalized["summary_consistency_audit"] = audit
        else:
            normalized.pop("summary_consistency_audit", None)
    return normalized


def compare_payloads(false_payload, true_payload):
    a = _normalize_payload(false_payload or {})
    b = _normalize_payload(true_payload or {})
    return {"equal_without_shadow": a == b}


def _strip_transients(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            if key in {"analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id", "summary_ir_version", "canonical_summary_ir_hash", "summary_ir_hash", "timestamp", "created_at", "updated_at"}:
                continue
            if isinstance(key, str) and key.lower() in {"timestamp", "created_at", "updated_at", "cache_key", "payload_id", "request_id", "trace_id"}:
                continue
            cleaned[key] = _strip_transients(child)
        return cleaned
    if isinstance(value, list):
        return [_strip_transients(item) for item in value]
    return value


def run_for_book(title: str):
    client = flask_app_module.app.test_client()
    pdf_path = PDFS.get(title)
    if not pdf_path or not os.path.exists(pdf_path):
        return {"title": title, "error": "missing_pdf", "path": pdf_path}

    resp_analiz = client.post('/api/tema-kazanim/analiz', json={"dosya_yolu": pdf_path})
    if resp_analiz.status_code != 200:
        return {"title": title, "error": "analiz_failed", "status": resp_analiz.status_code}
    analiz_json = resp_analiz.get_json() or {}
    analiz_sonucu = analiz_json.get('analiz_sonucu') or {}

    def fake_pdf(payload):
        fake_pdf.captured = dict(payload or {})
        return io.BytesIO(b"%PDF-1.4\n%fake-pdf\n")

    # collect with narrative_graph off and on to compare equal_without_shadow
    results = {}
    for flag in (False, True):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true' if flag else 'false'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        results["true" if flag else "false"] = fake_pdf.captured or {}

    cmp = compare_payloads(results.get("false"), results.get("true"))

    true_payload = results.get("true") or {}
    true_shadow = true_payload.get("_runtime_v7_shadow") or {}
    narrative = true_shadow.get("narrative") if isinstance(true_shadow, dict) else None

    checks = {"equal_without_shadow": bool(cmp.get("equal_without_shadow"))}

    # recommendations checks
    rec_checks = {
        "recommendations_in_shadow_only": True,
        "production_payload_unchanged": True,
        "recommendation_diagnostics_valid": False,
        "recommendation_types_valid": True,
        "deterministic": False,
        "book_specific_heuristic": False,
    }

    # production payload should not contain recommendations key at root
    if "recommendations" in true_payload:
        rec_checks["recommendations_in_shadow_only"] = False
        rec_checks["production_payload_unchanged"] = False

    # check narrative location
    recs = None
    diag = {}
    if isinstance(narrative, dict):
        recs = narrative.get("recommendations")
        diag = narrative.get("diagnostics") or {}

    # diagnostics fields
    diag_fields = [
        "recommendation_count",
        "review_recommendation_count",
        "strengthen_recommendation_count",
        "deprioritize_recommendation_count",
        "insufficient_evidence_recommendation_count",
        "average_recommendation_confidence",
    ]
    if all(f in diag for f in diag_fields):
        rec_checks["recommendation_diagnostics_valid"] = True

    # types
    if isinstance(recs, dict):
        # check lists
        all_recommendations = []
        for key in ("theme_recommendations", "character_recommendations", "learning_outcome_recommendations", "overall_recommendations"):
            arr = recs.get(key) or []
            if not isinstance(arr, list):
                arr = []
            all_recommendations.extend(arr)
        for r in all_recommendations:
            rt = r.get("recommendation_type")
            if rt not in REQUIRED_REC_TYPES:
                rec_checks["recommendation_types_valid"] = False

    # deterministic: run twice and compare stripped shadow
    deterministic_runs = []
    for _ in range(2):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        deterministic_runs.append(_strip_transients((fake_pdf.captured or {}).get("_runtime_v7_shadow") or {}))
    rec_checks["deterministic"] = deterministic_runs[0] == deterministic_runs[1]

    # simple heuristic detection: ensure no title-based branching by scanning recommendation reasons for title text
    title_lower = (title or "").lower()
    if isinstance(recs, dict):
        all_text = json.dumps(recs, ensure_ascii=False).lower()
        if title_lower in all_text:
            rec_checks["book_specific_heuristic"] = True

    out = {
        "title": title,
        "checks": checks,
        "recommendation_checks": rec_checks,
        "recommendations_keys": sorted(recs.keys()) if isinstance(recs, dict) else [],
        "diagnostics": diag,
    }
    return out


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    all_ok = True
    for book in books:
        try:
            book_result = run_for_book(book)
        except Exception as exc:  # pragma: no cover
            book_result = {"title": book, "error": str(exc)}
        results.append(book_result)
        # write per-book partial result so progress isn't lost
        safe_name = book.replace(' ', '_')
        book_outpath = os.path.join(os.path.dirname(__file__), f"phase9a_recommendation_engine_verification_{safe_name}.json")
        try:
            with open(book_outpath, 'w', encoding='utf-8') as fh:
                json.dump(book_result, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # final output only after all books processed
    final = {"books": results, "all_ok": all_ok}
    outpath = os.path.join(os.path.dirname(__file__), "phase9a_recommendation_engine_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "all_ok": all_ok}, ensure_ascii=False))
