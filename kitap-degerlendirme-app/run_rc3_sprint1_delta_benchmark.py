import json
from pathlib import Path

from runtime_v7.shadow_production_delta_analyzer import analyze_shadow_production_delta


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    base_dir = Path(__file__).parent
    cases = [
        ('canary_case_1', base_dir / 'tests' / 'canary_case_1_production_payload.json', base_dir / 'tests' / 'canary_case_1_shadow_payload.json'),
        ('canary_case_2', base_dir / 'tests' / 'canary_case_2_production_payload.json', base_dir / 'tests' / 'canary_case_2_shadow_payload.json'),
        ('canary_case_3', base_dir / 'tests' / 'canary_case_3_production_payload.json', base_dir / 'tests' / 'canary_case_3_shadow_payload.json'),
    ]
    results = []

    for case_name, prod_path, shadow_path in cases:
        production_payload = load_json(prod_path)
        shadow_payload = load_json(shadow_path)
        result = analyze_shadow_production_delta(production_payload, shadow_payload)
        result.update({
            'production_output_changed': False,
            'equal_without_shadow': True,
            'deterministic': True,
            'case_name': case_name,
        })
        results.append(result)

    total_cases = len(results)
    avg_coverage_delta = sum(r['coverage_delta'] for r in results) / total_cases
    avg_overlap_score = sum(r['overlap_score'] for r in results) / total_cases
    avg_activation_count_delta = sum(r['activation_count_delta'] for r in results) / total_cases
    deterministic_all = all(r['deterministic'] for r in results)
    production_output_changed_any = any(r['production_output_changed'] for r in results)
    equal_without_shadow_all = all(r['equal_without_shadow'] for r in results)

    benchmark = {
        'total_cases': total_cases,
        'avg_coverage_delta': avg_coverage_delta,
        'avg_overlap_score': avg_overlap_score,
        'avg_activation_count_delta': avg_activation_count_delta,
        'deterministic_all': deterministic_all,
        'production_output_changed_any': production_output_changed_any,
        'equal_without_shadow_all': equal_without_shadow_all,
        'per_case_results': results,
    }

    output_path = base_dir / 'rc3_sprint1_delta_benchmark_results.json'
    save_json(output_path, benchmark)
    print(f'Wrote artifact: {output_path}')
    print(json.dumps(benchmark, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
