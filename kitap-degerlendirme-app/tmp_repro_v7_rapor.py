import os
import json
from pathlib import Path
from app import app

os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'

book_name = 'Gökyüzünü Kaybeden Şehir'
path = Path(app.root_path) / 'uploads' / 'gokyuzunu_kaybeden_sehir.pdf'
print('PDF PATH', path)
print('EXISTS', path.exists())
with app.test_client() as client:
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': str(path), 'ozet_turu': 'standart', 'yas_grubu': '9-12'})
    print('ANALIZ_STATUS', resp.status_code)
    try:
        j = resp.get_json(silent=True)
    except Exception as e:
        j = None
        print('ANALIZ_JSON_ERROR', e)
    print('ANALIZ_JSON_TYPE', type(j).__name__)
    if isinstance(j, dict):
        print(json.dumps({k: j.get(k) for k in ['basarili', 'hata'] if k in j}, ensure_ascii=False, indent=2))
        sc = j.get('analiz_sonucu') or {}
    else:
        print('ANALIZ_BODY', resp.get_data(as_text=True)[:2000])
        sc = {}
    print('SC_KEYS', sorted(sc.keys()))
    for key in ['canonical_summary', 'canonical_summary_ir', 'canonical_summary_ir_hash', 'summary_ui', 'summary_pdf', 'summary_consistency_audit', 'ozet_kalite_kontrol']:
        if key in sc:
            print(f'{key}:', type(sc[key]).__name__)
            if key == 'canonical_summary_ir':
                print('  summary_ir_keys:', sorted(sc[key].keys()))
    r = client.post('/api/tema-kazanim/rapor', json={'analiz_sonucu': sc}, query_string={'format': 'pdf'})
    print('R_STATUS', r.status_code)
    print('R_CONTENT_TYPE', r.headers.get('Content-Type'))
    try:
        body = r.get_data(as_text=True)
        print('R_BODY', body[:8000])
    except Exception as e:
        print('R_GET_DATA_ERROR', repr(e))
        raise
