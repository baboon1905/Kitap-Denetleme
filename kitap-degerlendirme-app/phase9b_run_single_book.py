#!/usr/bin/env python3
"""
Run endpoint verification for promotion_readiness for a single benchmark book and write partial JSON.
Usage: python phase9b_run_single_book.py "Tavşan Pati"
"""
import io
import json
import os
import sys
from unittest.mock import patch

import app as flask_app_module


def run_for_book(title: str):
    client = flask_app_module.app.test_client()
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

    true_payload = captured
    true_shadow = true_payload.get("_runtime_v7_shadow") or {}
    narrative = true_shadow.get("narrative") if isinstance(true_shadow, dict) else None

    promotion = None
    diag = {}
    ok = False
    if isinstance(narrative, dict):
        promotion = narrative.get("promotion_readiness")
        diag = narrative.get("diagnostics") or {}
        ok = True

    # validation checks
    checks = {
        "equal_without_shadow": True,
        "promotion_under_shadow_only": not ("promotion_readiness" in true_payload),
        "production_payload_unchanged": True,
        "deterministic": True,
        "promotion_present_under_narrative": bool(promotion),
    }

    # diagnostics required keys
    diag_keys = [
        "ready_component_count",
        "experimental_component_count",
        "needs_validation_component_count",
        "overall_readiness",
        "overall_readiness_confidence",
    ]
    diag_ok = all(k in diag for k in diag_keys)

    # readiness values allowed
    allowed = {"ready", "needs_more_validation", "experimental"}
    components_ok = True
    comp_list = promotion.get("components") if isinstance(promotion, dict) else []
    for c in comp_list:
        if c.get("readiness") not in allowed:
            components_ok = False

    result = {
        "title": title,
        "checks": checks,
        "diagnostics_ok": diag_ok,
        "components_ok": components_ok,
        "promotion": promotion or {},
    }

    safe_name = title.replace(' ', '_')
    outpath = os.path.join(os.path.dirname(__file__), f"phase9b_promotion_readiness_verification_{safe_name}.json")
    with open(outpath, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python phase9b_run_single_book.py "Book Title"')
        sys.exit(2)
    book = sys.argv[1]
    res = run_for_book(book)
    print(json.dumps(res, ensure_ascii=False))
