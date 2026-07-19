from __future__ import annotations
import json
import os
import sys
import time

sys.path.insert(0, os.getcwd())
from app import app

CASES = [
    {
        'title': 'Tavşan Pati',
        'path': r'uploads\\arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
        'author': 'Ozlem Aytek',
    },
    {
        'title': 'Büyülü Yastıklar',
        'path': r'uploads\\buyulu_yastiklar.pdf',
        'author': 'Test',
    },
    {
        'title': 'Benim Adım Kristof Kolomb',
        'path': r'uploads\\benim_adim_kristof_kolomb.pdf',
        'author': 'Test',
    },
    {
        'title': 'Gökyüzünü Kaybeden Şehir',
        'path': r'uploads\\gokyuzunu_kaybeden_sehir.pdf',
        'author': 'Test',
    },
]

RUNTIME_NAMES = [
    'runtime_3_pdf_template_final_payload.json',
    'runtime_2_build_pdf_report_input.json',
    'runtime_1_analyze_theme_gain_return.json',
]


def load_latest_payload():
    for name in RUNTIME_NAMES:
        if os.path.exists(name):
            try:
                with open(name, 'r', encoding='utf-8') as handle:
                    return json.load(handle)
            except Exception:
                continue
    return {}


def call_endpoint(client, url, payload):
    resp = client.post(url, json=payload)
    time.sleep(0.01)
    return {
        'status': resp.status_code,
        'mimetype': resp.mimetype,
        'bytes': len(resp.get_data()),
        'content_type': resp.headers.get('Content-Type', ''),
        'ok': resp.status_code == 200,
    }


def compute_snapshot(payload):
    got = {
        'canonical_summary_ir_hash': payload.get('canonical_summary_ir_hash'),
        'summary_ui_hash': payload.get('ui_summary_hash') or payload.get('summary_ui_hash'),
        'summary_pdf_hash': payload.get('pdf_summary_hash') or payload.get('summary_pdf_hash'),
        'teacher_summary_hash': payload.get('teacher_summary_hash'),
        'summary_source_function': (payload.get('summary_consistency_audit') or {}).get('summary_source_function'),
        'summary_ir_source_active': (payload.get('summary_consistency_audit') or {}).get('summary_source_function') == 'canonical_summary_ir',
        'has_summary_ui': 'summary_ui' in payload,
        'has_summary_pdf': 'summary_pdf' in payload,
        'has_teacher_summary': 'teacher_summary' in payload,
        'has_canonical_summary_ir': 'canonical_summary_ir' in payload,
        'summary_keys_present': sorted([k for k in [
            'canonical_summary',
            'summary_ui',
            'summary_pdf',
            'teacher_summary',
            'summary_before_gate',
            'summary_after_gate',
            'summary_rendered_to_ui',
            'summary_used_for_pdf',
        ] if k in payload]),
    }
    values = [
        got['summary_ui_hash'],
        got['summary_pdf_hash'],
        got['teacher_summary_hash'],
        got['canonical_summary_ir_hash'],
    ]
    normalized = [v for v in values if v is not None]
    got['all_summary_hashes_equal'] = len(set(normalized)) == 1 if normalized else None
    got['ui_pdf_equal'] = got['summary_ui_hash'] is not None and got['summary_pdf_hash'] is not None and got['summary_ui_hash'] == got['summary_pdf_hash']
    got['ui_teacher_equal'] = got['summary_ui_hash'] is not None and got['teacher_summary_hash'] is not None and got['summary_ui_hash'] == got['teacher_summary_hash']
    got['pdf_teacher_equal'] = got['summary_pdf_hash'] is not None and got['teacher_summary_hash'] is not None and got['summary_pdf_hash'] == got['teacher_summary_hash']
    return got


def run_case(case, flag_value):
    os.environ['V7_SUMMARY_IR_SOURCE'] = 'true' if flag_value else 'false'
    os.environ['V7_SHADOW_MODE'] = 'false'
    payload = {
        'format': 'pdf',
        'ozet_turu': 'ayrintili',
        'yas_grubu': '9-12',
        'dosya_yolu': case['path'],
        'analiz_sonucu': {
            'kitap_adi': case['title'],
            'yazar': case['author'],
            'dosya_adi': os.path.basename(case['path']),
            'dosya_yolu': case['path'],
        },
    }
    with app.test_client() as client:
        pdf_res = call_endpoint(client, '/api/tema-kazanim/rapor', payload)
        teacher_res = call_endpoint(client, '/api/theme-report/teacher-pdf', payload)
        word_payload = dict(payload)
        word_payload['format'] = 'word'
        word_res = call_endpoint(client, '/api/tema-kazanim/rapor', word_payload)
    runtime_payload = load_latest_payload()
    snapshot = compute_snapshot(runtime_payload)
    snapshot.update({
        'pdf_endpoint': pdf_res,
        'teacher_endpoint': teacher_res,
        'word_endpoint': word_res,
        'status_ok': pdf_res['ok'] and teacher_res['ok'] and word_res['ok'],
        'title': case['title'],
    })
    return snapshot


def main():
    results = {}
    for flag in (False, True):
        key = 'V7_SUMMARY_IR_SOURCE_TRUE' if flag else 'V7_SUMMARY_IR_SOURCE_FALSE'
        results[key] = [run_case(case, flag) for case in CASES]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
