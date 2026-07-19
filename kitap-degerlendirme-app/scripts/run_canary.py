import os, io, json
from unittest.mock import patch
import app as flask_app_module

os.environ['RC2_STAGE2_2_WIRE_MONITOR'] = 'true'
os.environ['V7_SHADOW_MODE'] = 'true'

base = os.path.dirname(flask_app_module.__file__)
selected = os.path.join(base, 'uploads', '03_cokbilmis_alingan.pdf')
client = flask_app_module.app.test_client()

resp = client.post('/api/tema-kazanim/analiz', json={"dosya_yolu": selected})
if resp.status_code != 200:
    raise SystemExit(f'analiz failed {resp.status_code}')
analiz_sonucu = (resp.get_json() or {}).get('analiz_sonucu') or {}

# capture prepared and two true runs
captured = {}
def cap(name):
    def _cap(payload):
        captured[name] = dict(payload or {})
        return io.BytesIO(b"%PDF-FAKE\n")
    return _cap

with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=cap('false')):
    client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf", "v7_narrative_graph": False})
with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=cap('true1')):
    client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf", "v7_narrative_graph": True})
with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=cap('true2')):
    client.post('/api/tema-kazanim/rapor', json={"analiz_sonucu": analiz_sonucu, "format": "pdf", "v7_narrative_graph": True})

prepared_payload = captured.get('false') or {}
shadow_payload = captured.get('true1') or {}
shadow = (shadow_payload.get('_runtime_v7_shadow') or {})
pattern_activations = (shadow.get('semantic') or {}).get('pattern_activations') or []
monitoring = (shadow.get('semantic') or {}).get('monitoring') or {}

from rc2_sprint5_real_shadow_runner import _strip_transients
s1 = _strip_transients(shadow)
s2 = _strip_transients((captured.get('true2') or {}).get('_runtime_v7_shadow') or {})
deterministic = (s1 == s2)

# compute requested items
total = len(pattern_activations)
active = sum(1 for p in pattern_activations if p.get('status')=='active')
candidate = sum(1 for p in pattern_activations if p.get('status')=='candidate')
evidence_gt0 = sum(1 for p in pattern_activations if p.get('evidence_count',0)>0)
first_3 = pattern_activations[:3]

ver_path = os.path.join(base, 'rc2_sprint5_real_shadow_validation.json')
ver = {}
if os.path.exists(ver_path):
    with open(ver_path,'r',encoding='utf-8') as fh:
        ver = json.load(fh)

report = {
    '1_total': total,
    '2_active': active,
    '3_candidate': candidate,
    '4_evidence_gt0': evidence_gt0,
    '5_first_3': [{ 'pattern_id': a.get('pattern_id'), 'category': a.get('category'), 'status': a.get('status'), 'raw_confidence': a.get('raw_confidence'), 'calibrated_confidence': a.get('calibrated_confidence'), 'evidence_count': a.get('evidence_count')} for a in first_3],
    '6_equal_without_shadow': ver.get('equal_without_shadow'),
    '7_production_output_changed': ver.get('production_output_changed'),
    '8_deterministic': deterministic,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
