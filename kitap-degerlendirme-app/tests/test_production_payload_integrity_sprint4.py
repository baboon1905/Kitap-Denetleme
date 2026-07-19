import os
import json
import importlib.util


def load_monitor_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'runtime_v7', 'semantic_pattern_monitor.py')
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location('spm', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_verification_artifact_fields(tmp_path):
    mod = load_monitor_module()
    # create 74 dummy patterns
    patterns = [{'id': f'p{i}', 'category': 'theme'} for i in range(74)]
    matches = []
    out = mod.run_monitoring(patterns, matches, total_docs=10, output_prefix=str(tmp_path / 'rc2_sprint4'))
    vf = out['artifact_files']['verification']
    with open(vf, 'r', encoding='utf-8') as f:
        verification = json.load(f)

    expected_keys = [
        'production_output_changed', 'equal_without_shadow', 'deterministic',
        'book_specific_heuristics', 'new_endpoint_added', 'summary_ir_changed',
        'pdf_changed', 'teacher_report_changed', 'word_changed', 'total_patterns'
    ]

    for k in expected_keys:
        assert k in verification

    assert verification['production_output_changed'] is False
    assert verification['equal_without_shadow'] is True
    assert verification['deterministic'] is True
    assert verification['total_patterns'] == 74
