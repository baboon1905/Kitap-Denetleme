import os, sys, json
from copy import deepcopy

# Ensure project root is on sys.path so local modules import correctly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
  sys.path.insert(0, ROOT)

# Prepare sample minimal payload that should trigger a few patterns
sample = {
  'kitap_adi': 'Canary Book',
  'canonical_summary_ir': {
    'themes': ['macera ve keşif', 'dostluk ve yardim'],
    'learning_outcomes': ['okuduğunu anlama'],
  },
  'semantic': {},
  'narrative': {'summary': 'Bu bir macera hikayesi; dostluk önem kazanir.'}
}

# Run without gate
os.environ.pop('RC2_STAGE2_3_WIRE_PATTERN_PRODUCER', None)
from theme_gain_analysis import prepare_theme_report_payload
no_shadow = prepare_theme_report_payload(deepcopy(sample))

# Run with gate on
os.environ['RC2_STAGE2_3_WIRE_PATTERN_PRODUCER'] = 'true'
with_shadow_first = prepare_theme_report_payload(deepcopy(sample))
with_shadow_second = prepare_theme_report_payload(deepcopy(sample))

# Extract shadow outputs
shadow_first = with_shadow_first.get('_runtime_v7_shadow', {})
shadow_second = with_shadow_second.get('_runtime_v7_shadow', {})
activations = shadow_first.get('pattern_activations', [])
monitoring = shadow_first.get('pattern_monitoring', {})

# Metrics
pattern_activations_count = len(activations)
active_count = sum(1 for a in activations if a.get('status') == 'active')
evidence_count_positive = sum(1 for a in activations if a.get('evidence_count', 0) > 0)
first_three = activations[:3]

def strip_shadow(p):
    p2 = dict(p)
    p2.pop('_runtime_v7_shadow', None)
    return p2

equal_without_shadow = (strip_shadow(no_shadow) == strip_shadow(with_shadow_first))
production_output_changed = not equal_without_shadow
deterministic = (shadow_first == shadow_second)

report = {
  'pattern_activations_count': pattern_activations_count,
  'active_count': active_count,
  'evidence_count_positive': evidence_count_positive,
  'first_three_activations': first_three,
  'equal_without_shadow': equal_without_shadow,
  'production_output_changed': production_output_changed,
  'deterministic': deterministic,
  'pattern_monitoring': monitoring,
}

print(json.dumps(report, ensure_ascii=False, indent=2))
