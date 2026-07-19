import json
import os
from pathlib import Path

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

from app import app

BOOKS = [
    ('Büyülü Yastıklar', 'uploads/buyulu_yastiklar.pdf'),
    ('Benim Adım Kristof Kolomb', 'uploads/benim_adim_kristof_kolomb.pdf'),
]

RESULT_FILE = 'rerun_phase3b_two_books.json'


def short_body(response):
    try:
        if response.is_json:
            return json.dumps(response.get_json(), ensure_ascii=False)[:1000]
    except Exception:
        pass
    return response.get_data(as_text=True, errors='replace')[:1000]


def call_endpoint(client, url, json_payload, query_string=None):
    response = client.post(url, json=json_payload, query_string=query_string)
    return {
        'status': response.status_code,
        'ok': response.status_code == 200,
        'content_type': response.headers.get('Content-Type', ''),
        'short_body': None if response.status_code == 200 else short_body(response),
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


def run_book(book_name, relative_path):
    path = Path(app.root_path) / relative_path
    path = path.resolve()
    if not path.exists():
        return {'book': book_name, 'error': 'missing_pdf', 'path': str(path)}

    result = {'book': book_name, 'pdf_path': str(path), 'analiz': {}, 'endpoints': {}}

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
        result['analiz']['body'] = None if analiz_response.status_code == 200 else short_body(analiz_response)

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
            'summary_ui_hash': audit.get('summary_ui_hash'),
            'summary_pdf_hash': audit.get('summary_pdf_hash'),
            'teacher_summary_hash': audit.get('teacher_summary_hash'),
            'forbidden_summary_surfaces': analysis_payload.get('forbidden_summary_surfaces') or [],
            'summary_source_function': audit.get('summary_source_function'),
        })

        base_payload = {'analiz_sonucu': analysis_payload}

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


def main():
    summary = {'mode': 'V7_SUMMARY_IR_SOURCE=true', 'books': []}
    for book_name, path in BOOKS:
        print(f'Running: {book_name}')
        res = run_book(book_name, path)
        summary['books'].append(res)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f'Results written to {RESULT_FILE}')


if __name__ == '__main__':
    main()
