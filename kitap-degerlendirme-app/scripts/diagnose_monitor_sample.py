import json, os
base = os.path.dirname(os.path.dirname(__file__))
path = os.path.join(base, 'rc2_sprint5_monitor_sample.json')
with open(path, 'r', encoding='utf-8') as fh:
    data = json.load(fh)
pas = data.get('pattern_activations', [])
from collections import Counter
st = Counter([p.get('status') for p in pas])
evidence_gt0 = sum(1 for p in pas if p.get('evidence_count',0)>0)
raw_or_cal_gt0 = sum(1 for p in pas if (p.get('raw_confidence',0)>0 or p.get('calibrated_confidence',0)>0))
ids = set(p.get('pattern_id') for p in pas)
from runtime_v7.semantic_pattern_registry import get_sprint3_pattern_definitions
reg = get_sprint3_pattern_definitions()
reg_ids = set(p.get('id') for p in reg if isinstance(p, dict) and p.get('id'))
report = {
  'status_counts': dict(st),
  'evidence_count_gt0': evidence_gt0,
  'raw_or_cal_gt0': raw_or_cal_gt0,
  'pattern_count_in_sample': len(pas),
  'sample_ids_subset_of_registry': ids.issubset(reg_ids),
  'registry_count': len(reg_ids),
  'pattern_monitoring': data.get('pattern_monitoring', {}),
}
print(json.dumps(report, ensure_ascii=False, indent=2))
