import copy
import json
import os

import app as flask_app_module
import theme_gain_analysis

PDFS = {
    "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
    "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
    "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
}


def _normalize_payload(payload: dict) -> dict:
    payload = copy.deepcopy(payload or {})
    payload.pop("_runtime_v7_shadow", None)
    payload.pop("canonical_summary_ir", None)
    payload.pop("canonical_summary_ir_hash", None)
    for key in ("analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id"):
        payload.pop(key, None)
    audit = payload.get("summary_consistency_audit")
    if isinstance(audit, dict):
        audit = dict(audit)
        audit.pop("summary_ir_version", None)
        audit.pop("canonical_summary_ir_hash", None)
        if audit:
            payload["summary_consistency_audit"] = audit
        else:
            payload.pop("summary_consistency_audit", None)
    return payload


def _strip_transients(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, sub in value.items():
            if key in {"analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id", "summary_ir_version", "canonical_summary_ir_hash", "summary_ir_hash", "timestamp", "created_at", "updated_at"}:
                continue
            cleaned[key] = _strip_transients(sub)
        return cleaned
    if isinstance(value, list):
        return [_strip_transients(item) for item in value]
    return value


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
    return {"equal_without_shadow": not bool(diff_paths), "diff_paths": diff_paths}


def run_for_book(title: str):
    client = flask_app_module.app.test_client()
    pdf_path = PDFS.get(title)
    if not pdf_path or not os.path.exists(pdf_path):
        return {"title": title, "error": "missing_pdf", "path": pdf_path}

    resp = client.post('/api/tema-kazanim/analiz', json={"dosya_yolu": pdf_path})
    if resp.status_code != 200:
        return {"title": title, "error": "analiz_failed", "status": resp.status_code}
    analiz_json = resp.get_json() or {}
    analiz_sonucu = analiz_json.get('analiz_sonucu') or {}

    results = {}
    for flag in (False, True):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true' if flag else 'false'
        prepared = theme_gain_analysis.prepare_theme_report_payload(analiz_sonucu)
        results['true' if flag else 'false'] = prepared or {}

    true_payload = results.get('true') or {}
    shadow = true_payload.get('_runtime_v7_shadow') or {}
    narrative = shadow.get('narrative') or {}
    classification = narrative.get('story_arc_classification')

    deterministic_runs = []
    for _ in range(2):
        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        prepared = theme_gain_analysis.prepare_theme_report_payload(analiz_sonucu)
        deterministic_runs.append(_strip_transients((prepared or {}).get('_runtime_v7_shadow') or {}))

    return {
        "title": title,
        "compare": compare_payloads(results.get('false'), results.get('true')),
        "story_arc_classification": {
            "exists_in_shadow": isinstance(classification, dict),
            "arc_type": classification.get('arc_type') if isinstance(classification, dict) else None,
            "confidence": classification.get('confidence') if isinstance(classification, dict) else None,
            "signals": classification.get('signals') if isinstance(classification, dict) else None,
        },
        "production_payload_clean": {
            "story_arc_classification_top_level_absent": 'story_arc_classification' not in (results.get('true') or {}),
            "shadow_payload_present": '_runtime_v7_shadow' in (results.get('true') or {}),
        },
        "deterministic_shadow_output": {
            "stable_across_repeated_runs": deterministic_runs[0] == deterministic_runs[1] if len(deterministic_runs) >= 2 else None,
            "run_count": len(deterministic_runs),
        },
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    results = [run_for_book(book) for book in books]
    outpath = os.path.join(os.path.dirname(__file__), 'phase6c_story_arc_classification_verification.json')
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump({'books': results}, fh, ensure_ascii=False, indent=2)
    print(json.dumps({'result_file': outpath}, ensure_ascii=False))
