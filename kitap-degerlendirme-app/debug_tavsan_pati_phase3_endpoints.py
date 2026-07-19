import os
import json
from pprint import pprint

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

from app import app

PDF_PATH = os.path.join(app.root_path, 'uploads', 'arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf')


def main():
    client = app.test_client()
    print('[debug] calling /api/tema-kazanim/analiz')
    response = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': PDF_PATH})
    print('analiz status', response.status_code)
    print('analiz json keys', sorted(response.get_json().keys()) if response.is_json else 'not json')
    payload = response.get_json()
    print('analiz payload keys sample')
    if isinstance(payload, dict):
        for key in ['canonical_summary', 'summary_ui', 'summary_pdf', 'teacher_summary', 'canonical_summary_ir', 'canonical_summary_ir_hash', 'summary_consistency_audit', 'ozet_kalite_kontrol']:
            print(key, type(payload.get(key)), payload.get(key) if key in ['canonical_summary_ir_hash'] else '...')
    print()

    if response.status_code != 200:
        pprint(payload)
        return

    for endpoint, data in [
        ('/api/tema-kazanim/rapor?format=pdf', client.post('/api/tema-kazanim/rapor', json=payload, query_string={'format': 'pdf'})),
        ('/api/tema-kazanim/rapor?format=word', client.post('/api/tema-kazanim/rapor', json=payload, query_string={'format': 'word'})),
        ('/api/theme-report/teacher-pdf', client.post('/api/theme-report/teacher-pdf', json=payload)),
    ]:
        print(f'endpoint {endpoint} status', data.status_code)
        if data.is_json:
            print('json keys', sorted(data.get_json().keys()))
            pprint(data.get_json())
        else:
            print('response length', len(data.data))
        print()

if __name__ == '__main__':
    main()
