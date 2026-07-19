import io
import os
import sys
from pathlib import Path
from contextlib import redirect_stdout
from app import app

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

BOOKS = [
    ('Büyülü Yastıklar', 'uploads/buyulu_yastiklar.pdf'),
    ('Benim Adım Kristof Kolomb', 'uploads/benim_adim_kristof_kolomb.pdf'),
    ('Gökyüzünü Kaybeden Şehir', 'uploads/gokyuzunu_kaybeden_sehir.pdf'),
]

with app.test_client() as client:
    for name, rel_path in BOOKS:
        path = Path(app.root_path) / rel_path
        print('=== BOOK ===', name)
        print('PDF PATH:', path)
        print('EXISTS:', path.exists())
        fake_stdout = io.StringIO()
        with redirect_stdout(fake_stdout):
            resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': str(path), 'ozet_turu': 'standart', 'yas_grubu': '9-12'})
        print('ANALIZ_STATUS:', resp.status_code)
        if resp.is_json:
            j = resp.get_json()
            sc = j.get('analiz_sonucu') or {}
            print('  CANON_HASH:', sc.get('canonical_summary_ir_hash'))
            print('  SOURCE_FUNC:', (sc.get('summary_consistency_audit') or {}).get('summary_source_function'))
            print('  SUMMARY_UI_PRESENT:', 'summary_ui' in sc)
            print('  SUMMARY_PDF_PRESENT:', 'summary_pdf' in sc)
            print('  FORBIDDEN_IN_UI:', 'karabasan sorununa karsi cozum arayisi belirginlesir' in str(sc.get('summary_ui') or '').lower())
            print('  FORBIDDEN_IN_CANON:', 'karabasan sorununa karsi cozum arayisi belirginlesir' in str(sc.get('canonical_summary') or '').lower())
        else:
            print('  ANALIZ_BODY:', resp.get_data(as_text=True, errors='replace')[:800])
        for endpoint, params in [('/api/tema-kazanim/rapor', {'format': 'pdf'}), ('/api/tema-kazanim/rapor', {'format': 'word'}), ('/api/theme-report/teacher-pdf', None)]:
            r = client.post(endpoint, json={'analiz_sonucu': sc if isinstance(sc, dict) else {}}, query_string=params or {})
            print('  ENDPOINT:', endpoint, 'PARAMS:', params, 'STATUS:', r.status_code, 'CONTENT_TYPE:', r.headers.get('Content-Type'))
            if r.status_code != 200:
                print('   BODY:', r.get_data(as_text=True, errors='replace')[:1000])
        print('')
