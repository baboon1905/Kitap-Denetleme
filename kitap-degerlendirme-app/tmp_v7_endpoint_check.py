import os
from pathlib import Path
from app import app

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

BOOKS = [
    ('Büyülü Yastıklar', 'uploads/buyulu_yastiklar.pdf'),
    ('Benim Adım Kristof Kolomb', 'uploads/benim_adim_kristof_kolomb.pdf'),
]

with app.test_client() as client:
    for name, rel_path in BOOKS:
        path = Path(rel_path)
        print('=' * 80)
        print('BOOK:', name)
        print('PATH:', path, path.exists())
        resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': str(path), 'ozet_turu': 'standart', 'yas_grubu': '9-12'})
        print('ANALIZ status', resp.status_code)
        j = resp.get_json(silent=True)
        print('ANALIZ keys', list(j.keys()) if isinstance(j, dict) else None)
        if isinstance(j, dict):
            sc = j.get('analiz_sonucu') or {}
            print('  canonical_summary_ir_hash', sc.get('canonical_summary_ir_hash'))
            print('  summary_source', (sc.get('summary_consistency_audit') or {}).get('summary_source_function'))
            print('  canonical_summary starts', repr(str(sc.get('canonical_summary') or '')[:200]))
            print('  summary_ui starts', repr(str(sc.get('summary_ui') or '')[:200]))
            print('  contains forbidden summary_ui', 'karabasan sorununa karsi cozum arayisi belirginlesir' in str(sc.get('summary_ui') or '').lower())

            payload = {'analiz_sonucu': sc}
            for endpoint, params in [('/api/tema-kazanim/rapor', {'format': 'pdf'}), ('/api/tema-kazanim/rapor', {'format': 'word'}), ('/api/theme-report/teacher-pdf', None)]:
                r = client.post(endpoint, json=payload, query_string=params or {})
                print('  ENDPOINT', endpoint, 'params', params, 'status', r.status_code, 'content-type', r.headers.get('Content-Type'))
                if r.status_code != 200:
                    print('   body', r.get_data(as_text=True, errors='replace')[:1000])
        print()