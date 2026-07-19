import io
import json
import os
from unittest.mock import patch
import app as flask_app_module

pdf = r'c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app\uploads\arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf'
client = flask_app_module.app.test_client()
resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf})
analiz_sonucu = (resp.get_json() or {}).get('analiz_sonucu') or {}


def fake_pdf(payload):
    fake_pdf.captured = dict(payload or {})
    return io.BytesIO(b'%PDF-1.4\n%fake-pdf\n')

os.environ['V7_SHADOW_MODE'] = 'true'
os.environ['V7_NARRATIVE_GRAPH'] = 'true'
with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
    client.post('/api/tema-kazanim/rapor', json={'analiz_sonucu': analiz_sonucu, 'format': 'pdf'})
payload = fake_pdf.captured or {}
shadow = payload.get('_runtime_v7_shadow') or {}
narrative = shadow.get('narrative') if isinstance(shadow, dict) else None
print('has_validation_confidence', isinstance(narrative.get('validation_confidence'), dict) if isinstance(narrative, dict) else False)
print(json.dumps(narrative.get('validation_confidence'), ensure_ascii=False) if isinstance(narrative, dict) and isinstance(narrative.get('validation_confidence'), dict) else 'None')
print('production_has', 'validation_confidence' in payload)
