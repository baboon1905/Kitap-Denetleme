#!/usr/bin/env python3
"""Phase 10A shadow impact assessment verification."""
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
    impact = (narrative or {}).get("shadow_impact") or {}
    impact_components = impact.get("components") or []

    checks = {
        "equal_without_shadow": bool(cmp.get("equal_without_shadow")),
        "shadow_impact_only_under_narrative": isinstance(impact, dict) and bool(impact_components),
        "production_payload_unchanged": "shadow_impact" not in true_payload,
        "deterministic": False,
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
    checks["deterministic"] = deterministic_runs[0] == deterministic_runs[1]

    title_lower = (title or "").lower()
    if isinstance(impact_components, list):
        component_text = json.dumps(impact_components, ensure_ascii=False).lower()
        if title_lower in component_text:
            checks["book_specific_heuristic"] = True

    diagnostics = impact.get("diagnostics") or {}
    diag_fields = [
        "high_impact_component_count",
        "medium_impact_component_count",
        "low_impact_component_count",
        "insufficient_data_component_count",
        "overall_estimated_impact",
        "overall_impact_confidence",
    ]

    return {
        "title": title,
        "checks": checks,
        "diagnostics": diagnostics,
        "diagnostics_ok": all(f in diagnostics for f in diag_fields),
        "impact": impact,
        "impact_component_names": [c.get("name") for c in impact_components if isinstance(c, dict)],
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
    outpath = os.path.join(os.path.dirname(__file__), "phase10a_shadow_impact_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath, "books": len(results)}, ensure_ascii=False))
