import os
from pathlib import Path
os.environ['V7_SUMMARY_IR_SOURCE'] = 'true'
from app import app
from theme_gain_analysis import rapor_kalite_kapisi

path = Path('uploads/buyulu_yastiklar.pdf')
print('path exists', path.exists(), path)
with app.test_client() as client:
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': str(path), 'ozet_turu': 'standart', 'yas_grubu': '9-12'})
    print('status', resp.status_code)
    j = resp.get_json(silent=True)
    print('json type', type(j))
    print('keys', list(j.keys()) if isinstance(j, dict) else None)
    if isinstance(j, dict):
        sc = j.get('analiz_sonucu') or {}
        print('hash', sc.get('canonical_summary_ir_hash'))
        print('summary_source', (sc.get('summary_consistency_audit') or {}).get('summary_source_function'))
        print('canonical_summary starts', repr(str(sc.get('canonical_summary') or '')[:260]))
        print('summary_ui starts', repr(str(sc.get('summary_ui') or '')[:260]))
        print('has ir', isinstance(sc.get('canonical_summary_ir'), dict))
        print('ir hash', sc.get('canonical_summary_ir', {}).get('hash'))
        print('quality pass', rapor_kalite_kapisi(sc).get('gecerli'))
