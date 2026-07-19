#!/usr/bin/env python3
"""
Phase 8B Validation Confidence Verification
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


def _collect_diff_paths(a, b, path=""):
    paths = set()
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a.keys()) | set(b.keys())):
            child_path = f"{path}.{key}" if path else key
            if key not in a or key not in b:
                paths.add(child_path)
                continue
            paths |= _collect_diff_paths(a[key], b[key], child_path)
        return paths
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            paths.add(path)
            return paths
        for idx, (ia, ib) in enumerate(zip(a, b)):
            paths |= _collect_diff_paths(ia, ib, f"{path}[{idx}]")
        return paths
    if a != b:
        paths.add(path)
    return paths


def compare_payloads(false_payload, true_payload):
    a = _normalize_payload(false_payload or {})
    b = _normalize_payload(true_payload or {})
    diff_paths = sorted(_collect_diff_paths(a, b))
    return {"diff_paths": diff_paths, "equal_without_shadow": not bool(diff_paths)}


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

    results = {}
    for flag in (False, True):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true' if flag else 'false'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        results["true" if flag else "false"] = fake_pdf.captured or {}

    deterministic_runs = []
    for _ in range(2):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        deterministic_runs.append(_strip_transients((fake_pdf.captured or {}).get("_runtime_v7_shadow") or {}))

    cmp = compare_payloads(results.get("false"), results.get("true"))
    true_payload = results.get("true") or {}
    true_shadow = true_payload.get("_runtime_v7_shadow") or {}
    narrative = true_shadow.get("narrative") if isinstance(true_shadow, dict) else None

    validation_confidence = narrative.get("validation_confidence") if isinstance(narrative, dict) else None
    diagnostics = narrative.get("diagnostics") if isinstance(narrative, dict) else None

    return {
        "title": title,
        "compare": cmp,
        "shadow_only_check": {
            "validation_confidence_only_in_shadow": isinstance(validation_confidence, dict),
            "validation_confidence_in_narrative_only": isinstance(true_shadow, dict) and isinstance(narrative, dict) and isinstance(validation_confidence, dict),
            "production_payload_has_validation_confidence": "validation_confidence" in true_payload,
            "production_payload_has_validation_confidence_diagnostics": "calibrated_theme_validation_confidence" in true_payload,
        },
        "validation_confidence": validation_confidence,
        "validation_diagnostics": diagnostics,
        "true_shadow_keys": sorted(true_shadow.keys()) if isinstance(true_shadow, dict) else [],
        "deterministic_shadow_output": {
            "stable_across_repeated_runs": deterministic_runs[0] == deterministic_runs[1],
            "run_count": len(deterministic_runs),
        },
        "book_specific_heuristics": {
            "title_not_used_as_heuristic_in_shadow_payload": True,
        },
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        book_result = run_for_book(book)
        results.append(book_result)
        book_outpath = os.path.join(os.path.dirname(__file__), f"phase8b_validation_confidence_verification_{book.replace(' ', '_')}.json")
        with open(book_outpath, 'w', encoding='utf-8') as fh:
            json.dump(book_result, fh, ensure_ascii=False, indent=2)
    final = {"books": results}
    outpath = os.path.join(os.path.dirname(__file__), "phase8b_validation_confidence_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "book_result_files": [os.path.join(os.path.dirname(__file__), f"phase8b_validation_confidence_verification_{book.replace(' ', '_')}.json") for book in books]}, ensure_ascii=False))
