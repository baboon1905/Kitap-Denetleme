import os
import importlib.util


def load_monitor_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'runtime_v7', 'semantic_pattern_monitor.py')
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location('spm', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_quality_gates_rules():
    mod = load_monitor_module()
    patterns = [
        {'id': 'lowconf', 'category': 'theme'},
        {'id': 'highfp', 'category': 'theme'},
        {'id': 'dormant', 'category': 'structure'},
    ]

    # lowconf: many activations but low confidence -> review
    matches = []
    for i in range(5):
        matches.append({'pattern_id': 'lowconf', 'raw_confidence': 0.1, 'calibrated_confidence': 0.12, 'is_fp': False})

    # highfp: many activations and many fps -> watch/review
    for i in range(6):
        matches.append({'pattern_id': 'highfp', 'raw_confidence': 0.6, 'calibrated_confidence': 0.62, 'is_fp': True})

    res = mod.run_monitoring(patterns, matches, total_docs=10, output_prefix='rc2_sprint4_test')
    gates = res['quality_gates']
    assert 'lowconf' in gates['review']
    assert 'highfp' in gates['watch'] or 'highfp' in gates['review']
    assert 'dormant' in gates['dormant']
