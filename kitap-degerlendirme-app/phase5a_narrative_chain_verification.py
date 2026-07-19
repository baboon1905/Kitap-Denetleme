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
        os.environ['V7_SHADOW_MODE'] = "true"
        os.environ['V7_NARRATIVE_GRAPH'] = "true" if flag else "false"
        fake_pdf.captured = None
        with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
            resp = client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})
        captured = fake_pdf.captured or {}
        results["true" if flag else "false"] = captured

    cmp = compare_payloads(results.get("false"), results.get("true"))
    true_shadow = (results.get("true") or {}).get("_runtime_v7_shadow") or {}
    narrative = true_shadow.get("narrative") if isinstance(true_shadow, dict) else None
    narrative_checks = {}
    if isinstance(narrative, dict):
        narrative_chains = narrative.get("narrative_chains") or {}
        diag = narrative.get("diagnostics") or {}
        narrative_checks = {
            "has_narrative_chains": "narrative_chains" in narrative,
            "chain_count": narrative_chains.get("chain_count"),
            "largest_chain_size": narrative_chains.get("largest_chain_size"),
            "isolated_event_count": narrative_chains.get("isolated_event_count"),
            "average_chain_length": narrative_chains.get("average_chain_length"),
            "chain_confidence": narrative_chains.get("chain_confidence"),
            "diagnostics_keys": sorted([k for k in diag.keys()]) if isinstance(diag, dict) else [],
        }

    return {
        "title": title,
        "compare": cmp,
        "narrative_checks": narrative_checks,
        "true_shadow_keys": sorted(true_shadow.keys()) if isinstance(true_shadow, dict) else [],
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    final = {"books": [run_for_book(book) for book in books]}
    outpath = os.path.join(os.path.dirname(__file__), "phase5a_narrative_chain_verification.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"result_file": outpath}, ensure_ascii=False))
