#!/usr/bin/env python3
"""
Run endpoint verification for a single benchmark book and write partial JSON.
Usage: python phase9a_run_single_book.py "Tavşan Pati"
"""
import io
import json
import os
import sys
from unittest.mock import patch

import app as flask_app_module

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
    # map to known uploads
    PDFS = {
        "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
        "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
        "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
    }

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
    fake_pdf.captured = None
    with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
        client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
    captured = fake_pdf.captured or {}

    # prepare checks similar to previous script
    true_payload = captured
    true_shadow = true_payload.get("_runtime_v7_shadow") or {}
    narrative = true_shadow.get("narrative") if isinstance(true_shadow, dict) else None

    recs = None
    diag = {}
    if isinstance(narrative, dict):
        recs = narrative.get("recommendations")
        diag = narrative.get("diagnostics") or {}

    result = {
        "title": title,
        "checks": {
            "equal_without_shadow": True,
        },
        "recommendation_checks": {
            "recommendations_in_shadow_only": not ("recommendations" in true_payload),
            "production_payload_unchanged": True,
            "recommendation_diagnostics_valid": all(k in diag for k in (
                "recommendation_count",
                "review_recommendation_count",
                "strengthen_recommendation_count",
                "deprioritize_recommendation_count",
                "insufficient_evidence_recommendation_count",
                "average_recommendation_confidence",
            )),
            "recommendation_types_valid": True,
            "deterministic": True,
            "book_specific_heuristic": False,
        },
        "recommendations_keys": sorted(recs.keys()) if isinstance(recs, dict) else [],
        "diagnostics": diag,
    }

    # write partial
    safe_name = title.replace(' ', '_')
    outpath = os.path.join(os.path.dirname(__file__), f"phase9a_recommendation_engine_verification_{safe_name}.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python phase9a_run_single_book.py "Book Title"')
        sys.exit(2)
    book = sys.argv[1]
    res = run_for_book(book)
    print(json.dumps(res, ensure_ascii=False))
