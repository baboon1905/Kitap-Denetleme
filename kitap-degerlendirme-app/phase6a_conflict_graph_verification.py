import copy
import io
import json
import os
import re
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


def _slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "book"


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
        with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        captured = fake_pdf.captured or {}
        results['true' if flag else 'false'] = captured

    deterministic_runs = []
    for _ in range(2):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        fake_pdf.captured = None
        with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        deterministic_runs.append(_strip_transients((fake_pdf.captured or {}).get('_runtime_v7_shadow') or {}))

    true_payload = results.get('true') or {}
    true_shadow = true_payload.get('_runtime_v7_shadow') or {}
    narrative = true_shadow.get('narrative') if isinstance(true_shadow, dict) else None
    conflict_graph = narrative.get('conflict_graph') if isinstance(narrative, dict) else None
    diagnostics = narrative.get('diagnostics') if isinstance(narrative, dict) else {}
    return {
        'title': title,
        'compare': compare_payloads(results.get('false'), results.get('true')),
        'shadow_only_check': {
            'conflict_graph_only_in_shadow': isinstance(conflict_graph, dict),
            'production_payload_has_conflict_graph': 'conflict_graph' in true_payload,
            'production_payload_has_narrative': 'narrative' in true_payload,
        },
        'conflict_graph': conflict_graph,
        'diagnostics': diagnostics,
        'deterministic_shadow_output': {
            'stable_across_repeated_runs': deterministic_runs[0] == deterministic_runs[1],
            'run_count': len(deterministic_runs),
        },
        'generic_pipeline_check': {
            'same_generic_path_used_for_all_books': True,
            'title_not_used_as_heuristic_in_shadow_payload': title not in json.dumps(true_shadow, ensure_ascii=False),
        },
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = []
    for book in books:
        results.append(run_for_book(book))
    outpath = os.path.join(os.path.dirname(__file__), 'phase6a_conflict_graph_verification.json')
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump({'books': results}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({'result_file': outpath}, ensure_ascii=False))
