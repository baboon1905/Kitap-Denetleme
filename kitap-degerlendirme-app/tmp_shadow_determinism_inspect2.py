import os
import sys
import json
from pathlib import Path
sys.path.insert(0, os.getcwd())
import app
from runtime_v7.adapter import build_v7_shadow_payload

PDFS = {
    'Tavşan Pati': Path('uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf'),
    'Büyülü Yastıklar': Path('uploads/buyulu_yastiklar.pdf'),
    'Benim Adım Kristof Kolomb': Path('uploads/benim_adim_kristof_kolomb.pdf')
}

TRANSIENT_KEYS = {
    'analiz_tarihi', 'analysis_timestamp', 'cache_key', 'payload_id', 'summary_ir_version', 'canonical_summary_ir_hash', 'summary_ir_hash', 'timestamp', 'created_at', 'updated_at', 'checked_at'
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
        return [f'{path} type {type(a).__name__} != {type(b).__name__}']
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f'{path}.{k} missing in a' if path else f'{k} missing in a')
            elif k not in b:
                out.append(f'{path}.{k} missing in b' if path else f'{k} missing in b')
            else:
                out.extend(diff(a[k], b[k], f'{path}.{k}' if path else str(k)))
        return out
    if isinstance(a, list):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(diff(x, y, f'{path}[{i}]'))
        if len(a) != len(b):
            out.append(f'{path} len {len(a)} != {len(b)}')
        return out
    return [f'{path} {a!r} != {b!r}']


def analyze(path):
    print('ANALYZE', path)
    client = app.app.test_client()
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': str(path.resolve())})
    print('STATUS', resp.status_code)
    if resp.status_code != 200:
        print(resp.get_data(as_text=True)[:2000])
        raise RuntimeError('analysis failed')
    return resp.get_json().get('analiz_sonucu')


def compare(title, path):
    payload = analyze(path)
    os.environ['V7_NARRATIVE_GRAPH'] = 'true'
    s1 = build_v7_shadow_payload(payload)
    s2 = build_v7_shadow_payload(payload)
    s1 = strip_transients(s1)
    s2 = strip_transients(s2)
    equal = s1 == s2
    print('===', title, 'equal', equal)
    if not equal:
        d = diff(s1, s2)
        print('diff count', len(d))
        for line in d[:300]:
            print(line)
        if len(d) > 300:
            print('... diff truncated')
    return equal


if __name__ == '__main__':
    for title, path in PDFS.items():
        print(compare(title, path))
