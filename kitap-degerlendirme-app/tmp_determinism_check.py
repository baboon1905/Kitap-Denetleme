import os
import io
import json
from unittest.mock import patch
import app as flask_app_module

PDFS = {
    "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
    "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
    "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
}

TRANSIENT_KEYS = {
    "analiz_tarihi",
    "analysis_timestamp",
    "cache_key",
    "payload_id",
    "summary_ir_version",
    "canonical_summary_ir_hash",
    "summary_ir_hash",
    "timestamp",
    "created_at",
    "updated_at",
    "checked_at",
}


def strip_transients(value):
    if isinstance(value, dict):
        cleaned = {}
        for k, v in value.items():
            if k in TRANSIENT_KEYS:
                continue
            cleaned[k] = strip_transients(v)
        return cleaned
    if isinstance(value, list):
        return [strip_transients(item) for item in value]
    return value


def run_book(title):
    client = flask_app_module.app.test_client()
    pdf_path = PDFS[title]
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
    if resp.status_code != 200:
        print('ANALYSIS FAILED', title, resp.status_code)
        return
    analiz_sonucu = resp.get_json().get('analiz_sonucu') or {}

    def fake_pdf(payload):
        fake_pdf.captured = dict(payload or {})
        return io.BytesIO(b"%PDF-1.4\n%fake-pdf\n")

    os.environ['V7_SHADOW_MODE'] = 'true'
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'

    outputs = []
    for i in range(2):
        fake_pdf.captured = None
        with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={'analiz_sonucu': analiz_sonucu, 'format': 'pdf'})
        outputs.append(strip_transients((fake_pdf.captured or {}).get('_runtime_v7_shadow') or {}))

    equal = outputs[0] == outputs[1]
    print(title, 'equal=', equal)
    if not equal:
        s1 = json.dumps(outputs[0], sort_keys=True, ensure_ascii=False, indent=2).splitlines()
        s2 = json.dumps(outputs[1], sort_keys=True, ensure_ascii=False, indent=2).splitlines()
        import difflib
        for line in difflib.unified_diff(s1, s2, fromfile='first', tofile='second'):
            print(line)


if __name__ == '__main__':
    for title in PDFS:
        run_book(title)
