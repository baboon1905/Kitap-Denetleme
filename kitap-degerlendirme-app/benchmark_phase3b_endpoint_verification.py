import json
import os
from pathlib import Path
from pprint import pprint

os.environ.setdefault('V7_SUMMARY_IR_SOURCE', 'true')

from app import app

MODES = [
    ('V7_SUMMARY_IR_SOURCE=false', 'false'),
    ('V7_SUMMARY_IR_SOURCE=true', 'true'),
]

BOOKS = [
    ('Tavşan Pati', 'uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf'),
    ('Büyülü Yastıklar', 'uploads/buyulu_yastiklar.pdf'),
    ('Benim Adım Kristof Kolomb', 'uploads/benim_adim_kristof_kolomb.pdf'),
    ('Gökyüzünü Kaybeden Şehir', 'uploads/gokyuzunu_kaybeden_sehir.pdf'),
]

RESULT_FILE = 'benchmark_phase3b_endpoint_results.json'


def get_hash(payload, keys):
    if not isinstance(payload, dict):
        return None
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return value
    return None


def make_book_payload(analysis_result):
    return {
        'analiz_sonucu': analysis_result,
    }


def surface_consistency(audit):
    if not isinstance(audit, dict):
        return False
    required = [
        audit.get('summary_source_function') == 'canonical_summary_ir',
        bool(audit.get('canonical_summary_ir_hash')),
        bool(audit.get('summary_ui_hash')),
        bool(audit.get('summary_pdf_hash')),
        bool(audit.get('teacher_summary_hash')),
    ]
    return all(required)


def short_body(response):
    text = None
    if response.is_json:
        text = json.dumps(response.get_json(), ensure_ascii=False)
    else:
        text = response.get_data(as_text=True, errors='replace')
    return text[:1000]


def call_endpoint(client, url, json_payload, query_string=None):
    response = client.post(url, json=json_payload, query_string=query_string)
    return {
        'status': response.status_code,
        'ok': response.status_code == 200,
        'content_type': response.headers.get('Content-Type', ''),
        'short_body': short_body(response) if response.status_code != 200 else None,
    }


def run_book(book_name, relative_path):
    path = Path(app.root_path) / relative_path
    path = path.resolve()
    if not path.exists():
        return {
            'error': 'missing_pdf',
            'path': str(path),
        }

    result = {
        'book': book_name,
        'pdf_path': str(path),
        'analiz': {},
        'endpoints': {},
    }

    with app.test_client() as client:
        analiz_response = client.post('/api/tema-kazanim/analiz', json={
            'dosya_yolu': str(path),
            'ozet_turu': 'standart',
            'yas_grubu': '9-12',
        })
        result['analiz']['status'] = analiz_response.status_code
        if analiz_response.is_json:
            analiz_json = analiz_response.get_json()
        else:
            analiz_json = None
        result['analiz']['body'] = short_body(analiz_response) if analiz_response.status_code != 200 else None

        if analiz_response.status_code != 200:
            return result

        analysis_payload = analiz_json.get('analiz_sonucu') if isinstance(analiz_json, dict) else None
        if not isinstance(analysis_payload, dict):
            result['analiz']['error'] = 'missing_analiz_sonucu'
            return result

        audit = analysis_payload.get('summary_consistency_audit') or {}
        result['analiz'].update({
            'surface_consistency': surface_consistency(audit),
            'canonical_summary_ir_hash': analysis_payload.get('canonical_summary_ir_hash'),
            'summary_ui_hash': get_hash(audit, ['summary_ui_hash', 'summary_ui_hash']),
            'summary_pdf_hash': get_hash(audit, ['summary_pdf_hash', 'summary_pdf_hash']),
            'teacher_summary_hash': get_hash(audit, ['teacher_summary_hash', 'teacher_summary_hash']),
            'summary_source_function': audit.get('summary_source_function'),
        })

        base_payload = make_book_payload(analysis_payload)

        result['endpoints']['rapor_pdf'] = call_endpoint(
            client,
            '/api/tema-kazanim/rapor',
            {**base_payload, 'format': 'pdf'},
            query_string={'format': 'pdf'},
        )
        result['endpoints']['rapor_word'] = call_endpoint(
            client,
            '/api/tema-kazanim/rapor',
            {**base_payload, 'format': 'word'},
            query_string={'format': 'word'},
        )
        result['endpoints']['teacher_pdf'] = call_endpoint(
            client,
            '/api/theme-report/teacher-pdf',
            base_payload,
        )

    return result


if __name__ == '__main__':
    summary = {
        'modes': [],
    }

    for mode_name, mode_value in MODES:
        print('=' * 80)
        print(f'Running benchmark mode: {mode_name}')
        os.environ['V7_SUMMARY_IR_SOURCE'] = mode_value
        mode_results = {
            'flag_state': mode_name,
            'books': [],
        }
        for book_name, pdf_path in BOOKS:
            print(f'  Running benchmark for: {book_name}')
            book_result = run_book(book_name, pdf_path)
            mode_results['books'].append(book_result)
            print(json.dumps(book_result, ensure_ascii=False, indent=2))
            print('-' * 80)
        summary['modes'].append(mode_results)

    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f'Results written to {RESULT_FILE}')
