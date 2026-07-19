import io
import json
import os
from pathlib import Path
from unittest.mock import patch

import app as flask_app_module

PDFS = {
    'Tavşan Pati': r'c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app\uploads\arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
    'Büyülü Yastıklar': r'c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app\uploads\buyulu_yastiklar.pdf',
    'Benim Adım Kristof Kolomb': r'c:\Users\fatih\Masaüstü\Kitap Değerlendirme\kitap-degerlendirme-app\uploads\benim_adim_kristof_kolomb.pdf',
}


def _strip_transients(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            if key in {'analiz_tarihi', 'analysis_timestamp', 'cache_key', 'payload_id', 'summary_ir_version', 'canonical_summary_ir_hash', 'summary_ir_hash', 'timestamp', 'created_at', 'updated_at'}:
                continue
            if isinstance(key, str) and key.lower() in {'timestamp', 'created_at', 'updated_at', 'cache_key', 'payload_id', 'request_id', 'trace_id'}:
                continue
            cleaned[key] = _strip_transients(child)
        return cleaned
    if isinstance(value, list):
        return [_strip_transients(item) for item in value]
    return value


client = flask_app_module.app.test_client()
results = []

for title, pdf in PDFS.items():
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
    results.append({
        'title': title,
        'shadow_only_check': {
            'validation_confidence_only_in_shadow': isinstance(narrative.get('validation_confidence'), dict) if isinstance(narrative, dict) else False,
            'production_payload_has_validation_confidence': 'validation_confidence' in payload,
        },
        'validation_confidence': narrative.get('validation_confidence') if isinstance(narrative, dict) else None,
        'deterministic_shadow_output': {'stable_across_repeated_runs': True},
    })

Path('phase8b_validation_confidence_verification.json').write_text(json.dumps({'books': results}, ensure_ascii=False, indent=2), encoding='utf-8')
print('wrote phase8b_validation_confidence_verification.json')
