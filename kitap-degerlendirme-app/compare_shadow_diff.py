import os
import app as flask_app_module
import theme_gain_analysis
import json

PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(flask_app_module.__file__), 'uploads', 'debug_test_api_data.pdf'))

os.environ['V7_SHADOW_MODE'] = 'false'
resp = flask_app_module.app.test_client().post('/api/tema-kazanim/analiz', json={'dosya_yolu': PDF_PATH})
analiz = resp.get_json().get('analiz_sonucu', {})
false_p = theme_gain_analysis.prepare_theme_report_payload(analiz)

os.environ['V7_SHADOW_MODE'] = 'true'
true_p = theme_gain_analysis.prepare_theme_report_payload(analiz)

ignore = ['_runtime_v7_shadow', 'canonical_summary_ir', 'canonical_summary_ir_hash', 'summary_consistency_audit']
false_norm = {k: v for k, v in false_p.items() if k not in ignore}
true_norm = {k: v for k, v in true_p.items() if k not in ignore}

print('false payload keys', len(false_p), 'true payload keys', len(true_p))
print('false_norm keys', len(false_norm), 'true_norm keys', len(true_norm))
print('key diff', sorted(set(false_norm.keys()) ^ set(true_norm.keys())))

shared_keys = sorted(set(false_norm.keys()) & set(true_norm.keys()))
diffs = []
for k in shared_keys:
    f = false_norm[k]
    t = true_norm[k]
    try:
        if json.dumps(f, sort_keys=True, ensure_ascii=False) != json.dumps(t, sort_keys=True, ensure_ascii=False):
            diffs.append(k)
    except Exception:
        if f != t:
            diffs.append(k)
print('shared diff count', len(diffs))
print('shared diff keys sample', diffs[:50])

# Print first 50 changes with summary
for k in diffs[:50]:
    print('DIFF:', k)
    f = false_norm[k]
    t = true_norm[k]
    print('  false:', repr(f)[:200])
    print('  true :', repr(t)[:200])
