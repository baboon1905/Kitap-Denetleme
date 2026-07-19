import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from copy import deepcopy
from theme_gain_analysis import prepare_theme_report_payload

sample = {
  'kitap_adi': 'Gate Closed Canary',
  'canonical_summary_ir': {'themes': ['macera'], 'learning_outcomes': ['okuduğunu anlama']},
  'narrative': {'summary': 'Kisa bir macera.'}
}

# Ensure gate is OFF
os.environ.pop('RC2_STAGE2_3_WIRE_PATTERN_PRODUCER', None)

prepared = prepare_theme_report_payload(deepcopy(sample))
shadow = prepared.get('_runtime_v7_shadow')
has_shadow_activations = bool(shadow and shadow.get('pattern_activations'))

report = {
    'has_shadow_activations': has_shadow_activations,
    'shadow_present': '_runtime_v7_shadow' in prepared,
}

print(json.dumps(report, ensure_ascii=False, indent=2))
