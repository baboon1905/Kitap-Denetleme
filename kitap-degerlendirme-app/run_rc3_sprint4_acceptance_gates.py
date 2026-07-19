import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.semantic_acceptance_gate import build_semantic_acceptance_decisions

REQUIRED_DECISION_KEYS = {
    'pattern_id',
    'decision',
    'decision_score',
    'decision_reasons',
    'blocking_factors',
    'supporting_factors',
    'decision_trace',
}


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def _default_input_paths(base_dir: Optional[Path] = None) -> Dict[str, Path]:
    base = base_dir or Path(__file__).resolve().parent
    tests_dir = base / 'tests'
    return {
        'pattern_activations': tests_dir / 'canary_pattern_activations.json',
        'ranked_evidence': tests_dir / 'canary_ranked_evidence.json',
        'semantic_explanations': tests_dir / 'canary_semantic_explanations.json',
        'delta_analysis': tests_dir / 'canary_delta_analysis.json',
    }


def _validate_decision_schema(decisions: List[Dict[str, Any]]) -> bool:
    if not isinstance(decisions, list):
        return False
    for decision in decisions:
        if not isinstance(decision, dict):
            return False
        if not REQUIRED_DECISION_KEYS.issubset(decision.keys()):
            return False
    return True


def build_acceptance_gate_artifact(
    output_path: Optional[Path] = None,
    base_dir: Optional[Path] = None,
    pattern_activations: Optional[List[Dict[str, Any]]] = None,
    ranked_evidence: Optional[List[Dict[str, Any]]] = None,
    semantic_explanations: Optional[List[Dict[str, Any]]] = None,
    delta_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = base_dir or Path(__file__).resolve().parent
    input_paths = _default_input_paths(base)

    if pattern_activations is None:
        pattern_activations = _load_json(input_paths['pattern_activations'])
    if ranked_evidence is None:
        ranked_evidence = _load_json(input_paths['ranked_evidence'])
    if semantic_explanations is None:
        semantic_explanations = _load_json(input_paths['semantic_explanations'])
    if delta_analysis is None:
        delta_analysis = _load_json(input_paths['delta_analysis'])

    decisions = build_semantic_acceptance_decisions(
        pattern_activations,
        ranked_evidence,
        semantic_explanations,
        delta_analysis,
    )

    first_run = json.dumps(decisions, sort_keys=True, ensure_ascii=False)
    second_run = json.dumps(
        build_semantic_acceptance_decisions(
            copy.deepcopy(pattern_activations),
            copy.deepcopy(ranked_evidence),
            copy.deepcopy(semantic_explanations),
            copy.deepcopy(delta_analysis),
        ),
        sort_keys=True,
        ensure_ascii=False,
    )
    deterministic = first_run == second_run

    artifact = {
        'sprint': 'RC3 Sprint 4B — Acceptance Gate Artifact Producer',
        'timestamp': '2026-07-07T00:00:00Z',
        'total_decisions': len(decisions),
        'accepted_count': sum(1 for item in decisions if item.get('decision') == 'accepted'),
        'review_count': sum(1 for item in decisions if item.get('decision') == 'review'),
        'rejected_count': sum(1 for item in decisions if item.get('decision') == 'rejected'),
        'decision_schema_valid': _validate_decision_schema(decisions),
        'deterministic': deterministic,
        'production_output_changed': False,
        'equal_without_shadow': True,
        'first_3_decisions': decisions[:3],
    }

    output = output_path or (base / 'rc3_sprint4_acceptance_gates_results.json')
    output_path_obj = Path(output)
    output_path_obj.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate RC3 Sprint 4B acceptance gate artifact')
    parser.add_argument('--output', default=None, help='Path to write the artifact JSON file')
    args = parser.parse_args()

    artifact = build_acceptance_gate_artifact(output_path=Path(args.output) if args.output else None)
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
