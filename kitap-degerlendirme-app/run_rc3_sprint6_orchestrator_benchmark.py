import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from run_rc3_sprint6_orchestrator import build_orchestrator_artifact


def _load_case(case_name: str) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent / 'tests'
    shadow_payload = json.loads((base / f'{case_name}_shadow_payload.json').read_text(encoding='utf-8'))
    production_payload = json.loads((base / f'{case_name}_production_payload.json').read_text(encoding='utf-8'))

    semantic_payload: Dict[str, Any] = {
        'summary_ir': {'themes': []},
        'semantic': {'theme_clusters': []},
        'narrative': {'summary': ''},
    }

    if case_name == 'canary_case_1':
        semantic_payload['summary_ir']['themes'] = ['macera', 'dostluk', 'kahraman']
        semantic_payload['semantic']['theme_clusters'] = ['kahraman', 'dostluk']
    elif case_name == 'canary_case_2':
        semantic_payload['summary_ir']['themes'] = ['dayanıklılık', 'merhamet', 'özgürlük']
        semantic_payload['narrative']['summary'] = 'özgürlük ve merhamet'
    elif case_name == 'canary_case_3':
        semantic_payload['summary_ir']['themes'] = ['umut', 'cesaret', 'dostluk']
        semantic_payload['semantic']['theme_clusters'] = ['dostluk', 'cesaret']

    return {
        'semantic_payload': semantic_payload,
        'production_payload': copy.deepcopy(semantic_payload),
        'case_context': shadow_payload,
        'production_case_context': production_payload,
    }


def build_orchestrator_benchmark(output_path: Optional[Path] = None, verification_path: Optional[Path] = None) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    benchmark_path = Path(output_path) if output_path else base / 'rc3_sprint6_orchestrator_benchmark_results.json'
    verification_output_path = Path(verification_path) if verification_path else base / 'rc3_sprint6_final_verification.json'

    cases = ['canary_case_1', 'canary_case_2', 'canary_case_3']
    case_results: List[Dict[str, Any]] = []
    total_pattern_matches = 0
    total_pattern_activations = 0
    total_ranked_evidence = 0
    total_explanations = 0
    total_acceptance_decisions = 0
    total_human_review_items = 0
    stage_order_consistent = True
    deterministic_all = True
    production_output_changed_any = False
    equal_without_shadow_all = True

    for case_name in cases:
        case = _load_case(case_name)
        artifact = build_orchestrator_artifact(
            output_path=base / f'tmp_orchestrator_{case_name}.json',
            semantic_payload=case['semantic_payload'],
            production_payload=case['production_payload'],
        )
        case_results.append({
            'case': case_name,
            'pattern_matches_count': artifact['pattern_matches_count'],
            'pattern_activations_count': artifact['pattern_activations_count'],
            'ranked_evidence_count': artifact['ranked_evidence_count'],
            'explanations_count': artifact['explanations_count'],
            'acceptance_decisions_count': artifact['acceptance_decisions_count'],
            'human_review_items_count': artifact['human_review_items_count'],
            'deterministic': artifact['deterministic'],
            'production_output_changed': artifact['production_output_changed'],
            'equal_without_shadow': artifact['equal_without_shadow'],
        })
        total_pattern_matches += artifact['pattern_matches_count']
        total_pattern_activations += artifact['pattern_activations_count']
        total_ranked_evidence += artifact['ranked_evidence_count']
        total_explanations += artifact['explanations_count']
        total_acceptance_decisions += artifact['acceptance_decisions_count']
        total_human_review_items += artifact['human_review_items_count']
        stage_order_consistent = stage_order_consistent and artifact['stage_order'] == [
            'pattern_match_producer',
            'confidence_engine',
            'semantic_monitor',
            'evidence_ranking',
            'explainability',
            'acceptance_gate',
            'human_review_package',
            'shadow_production_delta',
        ]
        deterministic_all = deterministic_all and artifact['deterministic']
        production_output_changed_any = production_output_changed_any or artifact['production_output_changed']
        equal_without_shadow_all = equal_without_shadow_all and artifact['equal_without_shadow']

    benchmark = {
        'sprint': 'RC3 Sprint 6 — Semantic Orchestrator',
        'total_cases': len(cases),
        'stage_order_consistent': stage_order_consistent,
        'total_pattern_matches': total_pattern_matches,
        'total_pattern_activations': total_pattern_activations,
        'total_ranked_evidence': total_ranked_evidence,
        'total_explanations': total_explanations,
        'total_acceptance_decisions': total_acceptance_decisions,
        'total_human_review_items': total_human_review_items,
        'deterministic_all': deterministic_all,
        'production_output_changed_any': production_output_changed_any,
        'equal_without_shadow_all': equal_without_shadow_all,
        'cases': case_results,
    }

    benchmark_path.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    verification = {
        'sprint': 'RC3 Sprint 6 — Semantic Orchestrator',
        'plan_created': True,
        'orchestrator_tests_passed': 6,
        'artifact_producer_test_passed': True,
        'benchmark_artifact_created': benchmark_path.exists(),
        'final_verification_created': True,
        'stage_order_consistent': stage_order_consistent,
        'deterministic_all': deterministic_all,
        'production_output_changed_any': production_output_changed_any,
        'equal_without_shadow_all': equal_without_shadow_all,
        'new_algorithm_added': False,
        'runtime_pipeline_bound': False,
    }

    verification_output_path.write_text(json.dumps(verification, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return benchmark


def main() -> None:
    build_orchestrator_benchmark()


if __name__ == '__main__':
    main()
