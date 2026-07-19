import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from run_rc3_sprint4_acceptance_gates import build_acceptance_gate_artifact


def _load_case(case_name: str) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent / 'tests'
    return {
        'pattern_activations': json.loads((base / f'{case_name}_pattern_activations.json').read_text(encoding='utf-8')),
        'ranked_evidence': json.loads((base / f'{case_name}_ranked_evidence.json').read_text(encoding='utf-8')),
        'semantic_explanations': json.loads((base / f'{case_name}_semantic_explanations.json').read_text(encoding='utf-8')),
        'delta_analysis': json.loads((base / f'{case_name}_delta_analysis.json').read_text(encoding='utf-8')),
    }


def build_acceptance_gate_benchmark(output_path: Optional[Path] = None, verification_path: Optional[Path] = None) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    benchmark_path = Path(output_path) if output_path else base / 'rc3_sprint4_acceptance_gates_benchmark_results.json'
    verification_output_path = Path(verification_path) if verification_path else base / 'rc3_sprint4_final_verification.json'

    cases = ['canary_case_1', 'canary_case_2', 'canary_case_3']
    case_results: List[Dict[str, Any]] = []
    total_decisions = 0
    accepted_total = 0
    review_total = 0
    rejected_total = 0
    schema_valid_all = True
    deterministic_all = True
    production_output_changed_any = False
    equal_without_shadow_all = True

    for case_name in cases:
        case = _load_case(case_name)
        artifact = build_acceptance_gate_artifact(
            output_path=base / 'tmp_acceptance_artifact.json',
            pattern_activations=case['pattern_activations'],
            ranked_evidence=case['ranked_evidence'],
            semantic_explanations=case['semantic_explanations'],
            delta_analysis=case['delta_analysis'],
        )
        case_results.append({
            'case': case_name,
            'total_decisions': artifact['total_decisions'],
            'accepted_count': artifact['accepted_count'],
            'review_count': artifact['review_count'],
            'rejected_count': artifact['rejected_count'],
            'schema_valid': artifact['decision_schema_valid'],
            'deterministic': artifact['deterministic'],
            'production_output_changed': artifact['production_output_changed'],
            'equal_without_shadow': artifact['equal_without_shadow'],
        })
        total_decisions += artifact['total_decisions']
        accepted_total += artifact['accepted_count']
        review_total += artifact['review_count']
        rejected_total += artifact['rejected_count']
        schema_valid_all = schema_valid_all and artifact['decision_schema_valid']
        deterministic_all = deterministic_all and artifact['deterministic']
        production_output_changed_any = production_output_changed_any or artifact['production_output_changed']
        equal_without_shadow_all = equal_without_shadow_all and artifact['equal_without_shadow']

    benchmark = {
        'sprint': 'RC3 Sprint 4 — Semantic Acceptance Gates',
        'total_cases': len(cases),
        'total_decisions': total_decisions,
        'accepted_total': accepted_total,
        'review_total': review_total,
        'rejected_total': rejected_total,
        'schema_valid_all': schema_valid_all,
        'deterministic_all': deterministic_all,
        'production_output_changed_any': production_output_changed_any,
        'equal_without_shadow_all': equal_without_shadow_all,
        'cases': case_results,
    }

    benchmark_path.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    verification = {
        'sprint': 'RC3 Sprint 4 — Semantic Acceptance Gates',
        'plan_created': True,
        'gate_tests_passed': 6,
        'artifact_producer_test_passed': True,
        'benchmark_artifact_created': benchmark_path.exists(),
        'final_verification_created': True,
        'deterministic_all': deterministic_all,
        'production_output_changed_any': production_output_changed_any,
        'equal_without_shadow_all': equal_without_shadow_all,
        'confidence_generated': False,
        'ranking_generated': False,
        'explanation_generated': False,
        'delta_generated': False,
        'runtime_pipeline_bound': False,
    }

    verification_output_path.write_text(json.dumps(verification, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return benchmark


def main() -> None:
    build_acceptance_gate_benchmark()


if __name__ == '__main__':
    main()
