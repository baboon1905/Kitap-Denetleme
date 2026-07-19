import json
import os
from pathlib import Path
import importlib.util


def load_monitor_module():
    path = Path(__file__).resolve().parent.parent / 'runtime_v7' / 'semantic_pattern_monitor.py'
    spec = importlib.util.spec_from_file_location('spm', str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    base = Path(__file__).resolve().parent.parent
    # try app-level then workspace root
    candidates = [base / 'rc2_sprint3_semantic_pattern_library.json', base.parent / 'rc2_sprint3_semantic_pattern_library.json']
    lib_file = None
    for c in candidates:
        if c.exists():
            lib_file = c
            break
    if lib_file is None:
        raise FileNotFoundError('rc2_sprint3_semantic_pattern_library.json not found in expected locations')

    with open(lib_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    patterns_raw = data.get('patterns', {})
    patterns = []
    for pid, p in patterns_raw.items():
        patterns.append({'id': pid, 'category': p.get('category', 'uncategorized'), 'expected_density': p.get('expected_density', 0.0)})

    # Synthetic matches based on expected_density
    total_docs = 10
    matches = []
    for p in patterns:
        count = int(round(p.get('expected_density', 0.0) * total_docs))
        for i in range(count):
            matches.append({
                'pattern_id': p['id'],
                'raw_confidence': 0.5 + 0.5 * (p.get('expected_density', 0.0)),
                'calibrated_confidence': 0.5 + 0.5 * (p.get('expected_density', 0.0)) + 0.02,
                'is_fp': False if p.get('expected_density', 0.0) > 0.2 else True,
                'recommendation': 'keep' if p.get('expected_density', 0.0) > 0.3 else 'review',
            })

    mod = load_monitor_module()
    out = mod.run_monitoring(patterns, matches, total_docs=total_docs, output_prefix='rc2_sprint4')
    print('Artifacts written:')
    for k, v in out['artifact_files'].items():
        print(k, v)


if __name__ == '__main__':
    main()
