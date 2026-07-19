import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _iter_json_files():
    for p in ROOT.rglob('*.json'):
        # skip hidden and workspace files
        if any(part.startswith('.') for part in p.parts):
            continue
        yield p


def test_verification_files_do_not_contain_benchmark_results_key():
    verification_files = [p for p in _iter_json_files() if 'verification' in p.name.lower()]
    assert verification_files, "No verification files found to validate"
    for vf in verification_files:
        data = json.loads(vf.read_text(encoding='utf-8'))
        assert 'benchmark_results' not in data, f"Verification file {vf} must not contain top-level 'benchmark_results' content"


def test_benchmark_files_do_not_contain_verification_only_key():
    benchmark_files = [p for p in _iter_json_files() if 'benchmark' in p.name.lower()]
    assert benchmark_files, "No benchmark files found to validate"
    for bf in benchmark_files:
        data = json.loads(bf.read_text(encoding='utf-8'))
        assert 'verification_only' not in data, f"Benchmark file {bf} must not contain top-level 'verification_only' markers"


def test_verification_may_reference_benchmark_file_exists():
    verification_files = [p for p in _iter_json_files() if 'verification' in p.name.lower()]
    for vf in verification_files:
        data = json.loads(vf.read_text(encoding='utf-8'))
        ref = data.get('benchmark_results_file')
        if ref:
            refpath = (vf.parent / ref)
            assert refpath.exists(), f"Verification file {vf} references missing benchmark file: {ref}"
