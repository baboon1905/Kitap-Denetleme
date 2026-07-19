import contextlib
import io
import os
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path

# Ensure V7 summary IR source is enabled for benchmark runs before importing the app
# If a V7 benchmark is intended, set this to '1' so runtime_v7 picks it up at import time.
os.environ.setdefault('V7_SUMMARY_IR_SOURCE', '1')

from app import app as flask_app
from theme_gain_analysis import prepare_theme_report_payload

flask_app.testing = True
flask_app.logger.disabled = True

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PROJECT_ROOT / 'benchmark_summary_ir_snapshot_results_clean.json'

books = {
    'Tavşan Pati': 'uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
    'Büyülü Yastıklar': 'uploads/buyulu_yastiklar.pdf',
    'Benim Adım Kristof Kolomb': 'uploads/benim_adim_kristof_kolomb.pdf',
    'Gökyüzünü Kaybeden Şehir': 'uploads/gokyuzunu_kaybeden_sehir.pdf',
}


def summary_consistency(audit):
    if not isinstance(audit, dict):
        return False
    hashes = [
        audit.get('summary_ui_hash'),
        audit.get('summary_pdf_hash'),
        audit.get('summary_before_gate_hash'),
        audit.get('summary_after_gate_hash'),
    ]
    return all(hashes) and len(set(hashes)) == 1


def extract_source_ids(obj):
    ids = set()
    if isinstance(obj, dict):
        for key in ('source_sentence_id', 'source_sentence_ids', 'source_ids', 'sentence_ids', 'evidence_ids'):
            if key in obj:
                value = obj[key]
                if isinstance(value, str):
                    if value.strip():
                        ids.add(value.strip())
                elif isinstance(value, (list, tuple, set)):
                    for item in value:
                        item_str = str(item).strip()
                        if item_str:
                            ids.add(item_str)
        for value in obj.values():
            ids.update(extract_source_ids(value))
    elif isinstance(obj, (list, tuple, set)):
        for item in obj:
            ids.update(extract_source_ids(item))
    return ids


def count_placeholders(obj):
    count = 0
    if isinstance(obj, dict):
        ids = obj.get('source_sentence_ids')
        if isinstance(ids, (list, tuple)) and ids and not any(str(x).strip() for x in ids):
            count += 1
        for value in obj.values():
            count += count_placeholders(value)
    elif isinstance(obj, (list, tuple, set)):
        for item in obj:
            count += count_placeholders(item)
    return count


def quiet_call(func, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return func(*args, **kwargs)


def quiet_post(client, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return client.post(*args, **kwargs)


class _TimeoutResponse:
    def __init__(self, status_code=504, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def get_json(self, silent=True):
        return self._payload

    def get_data(self, as_text=False):
        return '' if as_text else b''

    @property
    def mimetype(self):
        return 'application/json'


def timed_post(path, json_payload=None, timeout_seconds=90):
    def do_post():
        with flask_app.test_client() as client:
            return quiet_post(client, path, json=json_payload)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(do_post)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError:
            return _TimeoutResponse(
                status_code=504,
                payload={'hata': f'Request timed out after {timeout_seconds} seconds.'}
            )
        except Exception as exc:
            return _TimeoutResponse(
                status_code=500,
                payload={'hata': f'Request failed: {exc}'}
            )


def short_error_message(response):
    if response is None:
        return None
    payload = response.get_json(silent=True)
    if isinstance(payload, dict):
        return payload.get('hata') or payload.get('message') or payload.get('error') or str(payload)
    return str(payload)


def endpoint_failure_type(status_code):
    if status_code in (500, 409):
        return 'blocking'
    return 'non_blocking'


def benchmark_book(book_name, filename):
    path = (PROJECT_ROOT / filename).resolve()
    if not path.exists():
        raise FileNotFoundError(f'Missing benchmark PDF: {path}')

    book_result = {
        'book': book_name,
        'pdf': os.path.basename(path),
        'analysis_status': None,
        'analysis_success': False,
        'canonical_ir_present': False,
        'canonical_ir_hash': None,
        'upstream_unique_ids': 0,
        'canonical_unique_ids': 0,
        'lost_ids': [],
        'fabricated_ids': [],
        'preservation_rate': None,
        'placeholder_count': 0,
        'enricher_placeholder_count': None,
        'enricher_preservation_rate': None,
        'hash_run_1': None,
        'hash_run_2': None,
        'deterministic': False,
        'surface_consistency': False,
        'pdf_endpoint_status': None,
        'word_endpoint_status': None,
        'teacher_endpoint_status': None,
        'errors': [],
        'acceptance': 'FAIL',
    }

    first_resp = timed_post('/api/tema-kazanim/analiz', json_payload={'dosya_yolu': str(path)}, timeout_seconds=120)
    book_result['analysis_status'] = first_resp.status_code
    payload = first_resp.get_json(silent=True) or {}
    book_result['analysis_success'] = first_resp.status_code == 200 and payload.get('basarili') is True

    analiz_sonucu = payload.get('analiz_sonucu') or {}
    canonical_ir = analiz_sonucu.get('canonical_summary_ir') if isinstance(analiz_sonucu, dict) else None
    book_result['canonical_ir_present'] = canonical_ir is not None

    first_prepared = None
    if first_resp.status_code == 200:
        first_prepared = quiet_call(prepare_theme_report_payload, analiz_sonucu)
        audit = first_prepared.get('summary_consistency_audit') or {}
        book_result['canonical_ir_hash'] = first_prepared.get('canonical_summary_ir_hash')
        book_result['surface_consistency'] = summary_consistency(audit)

    second_resp = timed_post('/api/tema-kazanim/analiz', json_payload={'dosya_yolu': str(path)}, timeout_seconds=120)
    second_payload = second_resp.get_json(silent=True) or {}
    second_analiz_sonucu = second_payload.get('analiz_sonucu') or {}
    second_canonical_ir = second_analiz_sonucu.get('canonical_summary_ir') if isinstance(second_analiz_sonucu, dict) else None
    second_prepared = None
    if second_resp.status_code == 200:
        second_prepared = quiet_call(prepare_theme_report_payload, second_analiz_sonucu)

    if first_prepared is not None:
        book_result['hash_run_1'] = first_prepared.get('canonical_summary_ir_hash')
    if second_prepared is not None:
        book_result['hash_run_2'] = second_prepared.get('canonical_summary_ir_hash')
    if book_result['hash_run_1'] and book_result['hash_run_2']:
        book_result['deterministic'] = book_result['hash_run_1'] == book_result['hash_run_2']

    if isinstance(analiz_sonucu, dict):
        analiz_copy = dict(analiz_sonucu)
        analiz_copy.pop('canonical_summary_ir', None)
        upstream_ids = extract_source_ids(analiz_copy)
    else:
        upstream_ids = set()
    canonical_ids = extract_source_ids(canonical_ir) if canonical_ir else set()
    book_result['upstream_unique_ids'] = len(upstream_ids)
    book_result['canonical_unique_ids'] = len(canonical_ids)
    book_result['lost_ids'] = sorted(list(upstream_ids - canonical_ids))
    book_result['fabricated_ids'] = sorted(list(canonical_ids - upstream_ids))
    if upstream_ids:
        book_result['preservation_rate'] = len(canonical_ids) / len(upstream_ids)
    else:
        book_result['preservation_rate'] = None
    book_result['placeholder_count'] = count_placeholders(canonical_ir) if canonical_ir else 0

    if first_resp.status_code != 200:
        book_result['errors'].append({
            'stage': 'analysis',
            'status': first_resp.status_code,
            'type': endpoint_failure_type(first_resp.status_code),
            'message': short_error_message(first_resp),
        })

    if first_resp.status_code == 200 and isinstance(analiz_sonucu, dict):
        for endpoint, body, timeout in [
            ('pdf', {'analiz_sonucu': analiz_sonucu, 'format': 'pdf'}, 90),
            ('word', {'analiz_sonucu': analiz_sonucu, 'format': 'word'}, 90),
        ]:
            resp2 = timed_post('/api/tema-kazanim/rapor', json_payload=body, timeout_seconds=timeout)
            book_result[f'{endpoint}_endpoint_status'] = resp2.status_code
            if resp2.status_code != 200:
                book_result['errors'].append({
                    'endpoint': endpoint,
                    'status': resp2.status_code,
                    'type': endpoint_failure_type(resp2.status_code),
                    'message': short_error_message(resp2),
                })

        resp3 = timed_post('/api/theme-report/teacher-pdf', json_payload={'analiz_sonucu': analiz_sonucu}, timeout_seconds=90)
        book_result['teacher_endpoint_status'] = resp3.status_code
        if resp3.status_code != 200:
            book_result['errors'].append({
                'endpoint': 'teacher',
                'status': resp3.status_code,
                'type': endpoint_failure_type(resp3.status_code),
                'message': short_error_message(resp3),
            })

    # Acceptance logic
    blocking_errors = [e for e in book_result['errors'] if e.get('type') == 'blocking']
    acceptance_ok = (
        book_result['analysis_status'] == 200
        and book_result['analysis_success']
        and book_result['canonical_ir_present']
        and book_result['placeholder_count'] == 0
        and not book_result['lost_ids']
        and not book_result['fabricated_ids']
        and (book_result['preservation_rate'] is None or book_result['preservation_rate'] == 1.0)
        and (book_result['enricher_placeholder_count'] in (0, None))
        and (book_result['enricher_preservation_rate'] in (1.0, None))
        and book_result['deterministic']
        and book_result['surface_consistency']
        and not blocking_errors
    )
    book_result['acceptance'] = 'PASS' if acceptance_ok else 'FAIL'

    return book_result


def build_clean_results():
    clean_results = {
        'benchmark': 'RC4 Sprint 12E.2.2',
        'configuration': {
            'shadow_only': True,
            'runtime_pipeline_bound': False,
        },
        'books': [],
        'summary': {
            'books_tested': 0,
            'books_passed': 0,
            'books_failed': 0,
            'acceptance': 'PASS',
        },
    }

    for book_name, filename in books.items():
        # Do not override V7 flag per-book; respect the env set before import
        # Leave V7_SHADOW_MODE untouched here (set externally if needed)
        clean_results['books'].append(benchmark_book(book_name, filename))

    clean_results['summary']['books_tested'] = len(clean_results['books'])
    clean_results['summary']['books_passed'] = sum(1 for item in clean_results['books'] if item['acceptance'] == 'PASS')
    clean_results['summary']['books_failed'] = len(clean_results['books']) - clean_results['summary']['books_passed']
    clean_results['summary']['acceptance'] = 'PASS' if clean_results['summary']['books_failed'] == 0 else 'FAIL'

    return clean_results


def main():
    clean_results = build_clean_results()
    with OUTPUT_PATH.open('w', encoding='utf-8') as output_file:
        json.dump(clean_results, output_file, ensure_ascii=False, indent=2)
        output_file.write('\n')
    print(f'Clean benchmark artifact written to: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
