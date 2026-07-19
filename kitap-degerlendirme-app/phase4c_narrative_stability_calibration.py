import os
import io
import json
import copy
from unittest.mock import patch

import app as flask_app_module


PDFS = {
    "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
    "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
    "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
}

METRICS = [
    "story_arc_type",
    "narrative_confidence",
    "main_arc_confidence",
    "arc_completeness_score",
    "weak_narrative_reason",
    "event_count",
    "meaningful_event_count",
    "generic_event_count",
    "placeholder_event_count",
    "connected_component_count",
]


def _capture_report_for(analiz_sonucu, v7_flag: bool):
    client = flask_app_module.app.test_client()

    def fake_pdf(payload):
        fake_pdf.captured = dict(payload or {})
        return io.BytesIO(b"%PDF-1.4\\n%fake-pdf\\n")

    os.environ['V7_SHADOW_MODE'] = "true"
    os.environ['V7_NARRATIVE_GRAPH'] = "true" if v7_flag else "false"

    fake_pdf.captured = None
    with patch.object(flask_app_module, "build_theme_pdf_report", side_effect=fake_pdf):
        resp = client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf"})

    captured = fake_pdf.captured or {}
    return captured, None


def run_book_stability(title: str):
    pdf_path = PDFS.get(title)
    if not pdf_path or not os.path.exists(pdf_path):
        return {"title": title, "error": "missing_pdf", "path": pdf_path}

    # run analiz once (heavy) and reuse for multiple rapor runs
    client = flask_app_module.app.test_client()
    resp_analiz = client.post('/api/tema-kazanim/analiz', json={"dosya_yolu": pdf_path})
    if resp_analiz.status_code != 200:
        return {"title": title, "error": "analiz_failed", "status": resp_analiz.status_code}
    analiz_json = resp_analiz.get_json() or {}
    analiz_sonucu = analiz_json.get('analiz_sonucu') or {}

    # baseline: run once with V7_NARRATIVE_GRAPH=false to compare equal_without_shadow
    false_payload, err = _capture_report_for(analiz_sonucu, False)
    if err:
        return {"title": title, **err}

    # run three times with V7_NARRATIVE_GRAPH=true
    runs = []
    for i in range(3):
        cap, err = _capture_report_for(analiz_sonucu, True)
        if err:
            return {"title": title, **err}
        runs.append(cap)

    # collect metrics per run
    extracted = []
    for cap in runs:
        shadow = (cap or {}).get("_runtime_v7_shadow") or {}
        narrative = shadow.get("narrative") if isinstance(shadow, dict) else None
        diag = (narrative or {}).get("diagnostics") or {}
        story_arc_type = (narrative or {}).get("story_arc", {}).get("type") if isinstance((narrative or {}).get("story_arc"), dict) else None
        row = {m: None for m in METRICS}
        row["story_arc_type"] = story_arc_type
        row["narrative_confidence"] = diag.get("narrative_confidence") if isinstance(diag, dict) else None
        for k in ("main_arc_confidence", "arc_completeness_score", "weak_narrative_reason", "event_count", "meaningful_event_count", "generic_event_count", "placeholder_event_count", "connected_component_count"):
            row[k] = diag.get(k) if isinstance(diag, dict) else None
        extracted.append(row)

    # determinism checks: all runs should be identical for each metric
    stable = True
    diffs = {}
    for m in METRICS:
        values = [r.get(m) for r in extracted]
        first = values[0]
        if any(v != first for v in values[1:]):
            stable = False
            diffs[m] = values

    # ensure no leakage of new fields into top-level production payload
    leaked = []
    top_level_keys_true = sorted((runs[0] or {}).keys()) if runs else []

    # compare false vs true payload ignoring _runtime_v7_shadow
    def _normalize(p):
        copy_p = copy.deepcopy(p or {})
        copy_p.pop("_runtime_v7_shadow", None)
        for transient in ("analiz_tarihi", "analysis_timestamp", "cache_key", "payload_id"):
            copy_p.pop(transient, None)
        return copy_p

    equal_without_shadow = (_normalize(false_payload) == _normalize(runs[0]))

    return {
        "title": title,
        "runs": extracted,
        "stable": stable,
        "diffs": diffs,
        "equal_without_shadow": equal_without_shadow,
        "top_level_keys_true": top_level_keys_true,
    }


if __name__ == '__main__':
    books = ["Tavşan Pati", "Büyülü Yastıklar", "Benim Adım Kristof Kolomb"]
    final = {"books": []}
    for b in books:
        final["books"].append(run_book_stability(b))

    outpath = os.path.join(os.path.dirname(__file__), "phase4c_narrative_stability_calibration.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, ensure_ascii=False, indent=2)

    print(json.dumps({"result_file": outpath}, ensure_ascii=False))
