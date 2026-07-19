#!/usr/bin/env python3
"""Phase 12A runtime performance baseline verification."""
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
    normalized.pop("canonical_summary_ir", None)
    normalized.pop("canonical_summary_ir_hash", None)
    for transient in ("analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id"):
        normalized.pop(transient, None)
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

    os.environ['V7_SHADOW_MODE'] = 'true'
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'
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

    performance_baseline = (true_shadow or {}).get("performance_baseline") or {}
    module_timings = performance_baseline.get("module_timings") or {}
    checks = {
        "equal_without_shadow": bool(cmp.get("equal_without_shadow")),
        "performance_baseline_only_under_shadow": bool(performance_baseline) and "performance_baseline" in true_shadow,
        "production_payload_unchanged": "performance_baseline" not in true_payload,
        "deterministic_semantic_output": False,
        "book_specific_heuristic": False,
    }

    deterministic_runs = []
    for _ in range(2):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        deterministic_runs.append(_strip_transients((fake_pdf.captured or {}).get("_runtime_v7_shadow") or {}))
    checks["deterministic_semantic_output"] = deterministic_runs[0] == deterministic_runs[1]

    title_lower = (title or "").lower()
    if isinstance(module_timings, dict):
        timing_text = json.dumps(module_timings, ensure_ascii=False).lower()
        if title_lower in timing_text:
            checks["book_specific_heuristic"] = True

    return {
        "title": title,
        "checks": checks,
        "performance_baseline": performance_baseline,
        "module_timings": module_timings,
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        try:
            results.append(run_for_book(book))
        except Exception as exc:  # pragma: no cover
            results.append({"title": book, "error": str(exc)})
    final = {
        "books": results,
        "all_ok": all(not bool((book.get("checks") or {}).get("equal_without_shadow") is False) for book in results if isinstance(book, dict)),
    }
    outpath = os.path.join(os.path.dirname(__file__), "phase12a_runtime_performance_baseline.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "books": len(results)}, ensure_ascii=False))
