import os
import importlib.util
import json


def load_monitor_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'runtime_v7', 'semantic_pattern_monitor.py')
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location('spm', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_monitoring_determinism(tmp_path):
    mod = load_monitor_module()
    patterns = [
        {'id': 'p1', 'category': 'theme'},
        {'id': 'p2', 'category': 'structure'},
    ]
    matches = [
        {'pattern_id': 'p1', 'raw_confidence': 0.5, 'calibrated_confidence': 0.52, 'is_fp': False},
    ]

    out1 = mod.run_monitoring(patterns, matches, total_docs=5, output_prefix=str(tmp_path / 'r1'))
    out2 = mod.run_monitoring(patterns, matches, total_docs=5, output_prefix=str(tmp_path / 'r2'))

    # Compare deterministic structures
    assert json.dumps(out1['pattern_metrics'], sort_keys=True) == json.dumps(out2['pattern_metrics'], sort_keys=True)
    assert json.dumps(out1['quality_gates'], sort_keys=True) == json.dumps(out2['quality_gates'], sort_keys=True)
