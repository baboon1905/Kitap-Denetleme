import json
import os
import importlib.util


def load_monitor_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'runtime_v7', 'semantic_pattern_monitor.py')
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location('spm', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_semantic_pattern_monitor_basic(tmp_path):
    mod = load_monitor_module()
    patterns = [
        {'id': 'p1', 'category': 'theme'},
        {'id': 'p2', 'category': 'structure'},
        {'id': 'p3', 'category': 'theme'},
    ]

    matches = [
        {'pattern_id': 'p1', 'raw_confidence': 0.9, 'calibrated_confidence': 0.92, 'is_fp': False, 'recommendation': 'keep'},
        {'pattern_id': 'p1', 'raw_confidence': 0.85, 'calibrated_confidence': 0.88, 'is_fp': False, 'recommendation': 'keep'},
        {'pattern_id': 'p2', 'raw_confidence': 0.2, 'calibrated_confidence': 0.25, 'is_fp': True, 'recommendation': 'review'},
    ]

    res = mod.run_monitoring(patterns, matches, total_docs=10, output_prefix=str(tmp_path / 'rc2_sprint4'))
    assert 'pattern_metrics' in res
    assert len(res['pattern_metrics']) == 3
    pm = {p['pattern_id']: p for p in res['pattern_metrics']}
    assert pm['p1']['match_count'] == 2
    assert pm['p2']['match_count'] == 1
    assert pm['p3']['match_count'] == 0
