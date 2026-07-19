import os
import io
import json
from unittest.mock import patch
import app as flask_app_module

PDFS = {
    'Tavşan Pati': os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), 'uploads', 'arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf')),
    'Büyülü Yastıklar': os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), 'uploads', 'buyulu_yastiklar.pdf')),
    'Benim Adım Kristof Kolomb': os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), 'uploads', 'benim_adim_kristof_kolomb.pdf')),
}

TRANSIENT_KEYS = {
    'analiz_tarihi', 'analysis_timestamp', 'cache_key', 'payload_id', 'summary_ir_version', 'canonical_summary_ir_hash', 'summary_ir_hash', 'timestamp', 'created_at', 'updated_at', 'checked_at',
}


def strip_transients(value):
    if isinstance(value, dict):
        return {k: strip_transients(v) for k, v in value.items() if k not in TRANSIENT_KEYS}
    if isinstance(value, list):
        return [strip_transients(v) for v in value]
    return value


def diff(a, b, path=''):
    if a == b:
        return []
    if type(a) != type(b):
        return [path + f' type {type(a).__name__} != {type(b).__name__}']
    if isinstance(a, dict):
        keys = set(a) | set(b)
        diffs = []
        for k in sorted(keys):
            if k not in a:
                diffs.append(path + f' +{k}')
            elif k not in b:
                diffs.append(path + f' -{k}')
            else:
                diffs.extend(diff(a[k], b[k], path + '.' + str(k) if path else str(k)))
        return diffs
    if isinstance(a, list):
        diffs = []
        for i, (x, y) in enumerate(zip(a, b)):
            diffs.extend(diff(x, y, path + f'[{i}]'))
        if len(a) != len(b):
            diffs.append(path + f' len {len(a)} != {len(b)}')
        return diffs
    return [path + f' {a!r} != {b!r}']


for title, pdf_path in PDFS.items():
    print('BOOK', title)
    client = flask_app_module.app.test_client()
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
    if resp.status_code != 200:
        print('ANALYSIS FAILED', resp.status_code)
        continue
    analiz_sonucu = resp.get_json().get('analiz_sonucu') or {}
    os.environ['V7_SHADOW_MODE'] = 'true'
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'

    def fake_pdf(payload):
        fake_pdf.captured = dict(payload or {})
        return io.BytesIO(b'%PDF-1.4\n%fake-pdf\n')

    outputs = []
    for i in range(2):
        fake_pdf.captured = None
        with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={'analiz_sonucu': analiz_sonucu, 'format': 'pdf'})
        outputs.append(strip_transients((fake_pdf.captured or {}).get('_runtime_v7_shadow') or {}))

    diffs = diff(outputs[0], outputs[1])
    print('equal:', len(diffs) == 0, 'diff count', len(diffs))
    for d in diffs[:500]:
        print(d)
    if len(diffs) > 500:
        print('... (truncated)', len(diffs), 'differences total')
