#!/usr/bin/env python3
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


def _normalize_payload(payload: dict) -> dict:
    normalized = copy.deepcopy(payload or {})
    normalized.pop("_runtime_v7_shadow", None)
    # keep canonical_summary_ir_hash for explicit check but remove the large structure
    csir = normalized.get("canonical_summary_ir")
    if csir is not None:
        normalized["canonical_summary_ir"] = "<present>"
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


def run_book_checks(title: str):
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

    results = {}
    for flag in (False, True):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true' if flag else 'false'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        results["true" if flag else "false"] = fake_pdf.captured or {}

    cmp_equal = _normalize_payload(results.get("false")) == _normalize_payload(results.get("true"))
    true_payload = results.get("true") or {}
    true_shadow = true_payload.get("_runtime_v7_shadow") or {}

    # classification presence
    classification = true_shadow.get("classification") if isinstance(true_shadow, dict) else None

    # production leak: classification must not be top-level
    production_leak = "classification" in true_payload

    # summary ir stability: compare canonical_summary_ir_hash if available
    hash_false = (results.get("false") or {}).get("canonical_summary_ir_hash")
    hash_true = (results.get("true") or {}).get("canonical_summary_ir_hash")
    summary_ir_unchanged = hash_false == hash_true

    # endpoints check
    pdf_response = client.post('/api/tema-kazanim/rapor', json=results.get("true"))
    word_response = client.post('/api/tema-kazanim/rapor', json=results.get("true"), query_string={"format": "word"})
    teacher_response = client.post('/api/theme-report/teacher-pdf', json=results.get("true"))

    # deterministic shadow check
    deterministic_runs = []
    for _ in range(2):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        deterministic_runs.append(_strip_transients((fake_pdf.captured or {}).get("_runtime_v7_shadow") or {}))
    deterministic = deterministic_runs[0] == deterministic_runs[1]

    # book-specific heuristic check
    title_lower = (title or "").lower()
    impact = (true_shadow.get("narrative") or {}).get("shadow_impact") or {}
    components = impact.get("components") or []
    book_specific = False
    if isinstance(components, list):
        component_text = json.dumps(components, ensure_ascii=False).lower()
        if title_lower in component_text:
            book_specific = True

    return {
        "title": title,
        "equal_without_shadow": bool(cmp_equal),
        "classification_present": bool(classification),
        "classification": classification,
        "production_leak": bool(production_leak),
        "summary_ir_unchanged": bool(summary_ir_unchanged),
        "endpoints": {"pdf": pdf_response.status_code, "word": word_response.status_code, "teacher": teacher_response.status_code},
        "deterministic": bool(deterministic),
        "book_specific_heuristic": bool(book_specific),
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    out = {"timestamp": __import__('datetime').datetime.now().isoformat(), "books": {}}
    client = flask_app_module.app.test_client()
    for book in books:
        try:
            out["books"][book] = run_book_checks(book)
        except Exception as exc:  # pragma: no cover
            out["books"][book] = {"error": str(exc)}

    outpath = os.path.join(os.path.dirname(__file__), "rc11_fix3_classification_benchmark_results.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "books": len(books)}, ensure_ascii=False))
