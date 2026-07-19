import os
import json
import io
from unittest.mock import patch
import app as flask_app_module
from runtime_v7.adapter import build_v7_shadow_payload

PDFS = {
    "Tavşan Pati": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf")),
    "Büyülü Yastıklar": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "buyulu_yastiklar.pdf")),
    "Benim Adım Kristof Kolomb": os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), "uploads", "benim_adim_kristof_kolomb.pdf")),
}


def strip_transients(value):
    if isinstance(value, dict):
        cleaned = {}
        for k, v in value.items():
            if k in {
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
            }:
                continue
            cleaned[k] = strip_transients(v)
        return cleaned
    if isinstance(value, list):
        return [strip_transients(item) for item in value]
    return value


def analyze_book(title):
    client = flask_app_module.app.test_client()
    pdf_path = PDFS[title]
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
    if resp.status_code != 200:
        raise RuntimeError(f"Analysis failed for {title}: {resp.status_code}")
    return resp.get_json().get('analiz_sonucu') or {}


def build_shadow(payload):
    os.environ['V7_SHADOW_MODE'] = 'true'
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'
    return build_v7_shadow_payload(payload)


def compare_shadows(shadow1, shadow2):
    s1 = strip_transients(shadow1)
    s2 = strip_transients(shadow2)
    equal = s1 == s2
    print('equal:', equal)
    if not equal:
        import difflib
        s1_lines = json.dumps(s1, sort_keys=True, ensure_ascii=False, indent=2).splitlines()
        s2_lines = json.dumps(s2, sort_keys=True, ensure_ascii=False, indent=2).splitlines()
        for line in difflib.unified_diff(s1_lines, s2_lines, fromfile='first', tofile='second'):
            print(line)


if __name__ == '__main__':
    for title, path in PDFS.items():
        print('===', title)
        payload = analyze_book(title)
        shadow1 = build_shadow(payload)
        shadow2 = build_shadow(payload)
        compare_shadows(shadow1, shadow2)
