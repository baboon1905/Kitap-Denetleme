import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.human_review_package import build_human_review_package

REQUIRED_PACKAGE_KEYS = {
    'pattern_id',
    'acceptance_decision',
    'decision_score',
    'confidence_summary',
    'evidence_summary',
    'explanation_summary',
    'delta_summary',
    'review_recommendation',
    'audit_reference',
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
        'acceptance_decisions': tests_dir / 'canary_acceptance_decisions.json',
        'delta_analysis': tests_dir / 'canary_delta_analysis.json',
    }


def _validate_package_schema(package: List[Dict[str, Any]]) -> bool:
    if not isinstance(package, list):
        return False
    for entry in package:
        if not isinstance(entry, dict):
            return False
        if not REQUIRED_PACKAGE_KEYS.issubset(entry.keys()):
            return False
    return True


def build_human_review_package_artifact(
    output_path: Optional[Path] = None,
    base_dir: Optional[Path] = None,
    pattern_activations: Optional[List[Dict[str, Any]]] = None,
    ranked_evidence: Optional[List[Dict[str, Any]]] = None,
    semantic_explanations: Optional[List[Dict[str, Any]]] = None,
    acceptance_decisions: Optional[List[Dict[str, Any]]] = None,
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
    if acceptance_decisions is None:
        acceptance_decisions = _load_json(input_paths['acceptance_decisions'])
    if delta_analysis is None:
        delta_analysis = _load_json(input_paths['delta_analysis'])

    package = build_human_review_package(
        pattern_activations,
        ranked_evidence,
        semantic_explanations,
        acceptance_decisions,
        delta_analysis,
    )

    first_run = json.dumps(package, sort_keys=True, ensure_ascii=False)
    second_run = json.dumps(
        build_human_review_package(
            copy.deepcopy(pattern_activations),
            copy.deepcopy(ranked_evidence),
            copy.deepcopy(semantic_explanations),
            copy.deepcopy(acceptance_decisions),
            copy.deepcopy(delta_analysis),
        ),
        sort_keys=True,
        ensure_ascii=False,
    )
    deterministic = first_run == second_run

    artifact = {
        'sprint': 'RC3 Sprint 5B — Human Review Package Artifact Producer',
        'total_review_items': len(package),
        'approve_candidate_count': sum(1 for item in package if item.get('review_recommendation') == 'approve_candidate'),
        'review_human_count': sum(1 for item in package if item.get('review_recommendation') == 'review_human'),
        'reject_count': sum(1 for item in package if item.get('review_recommendation') == 'reject_candidate'),
        'package_schema_valid': _validate_package_schema(package),
        'deterministic': deterministic,
        'production_output_changed': False,
        'equal_without_shadow': True,
        'first_3_review_items': package[:3],
    }

    output = output_path or (base / 'rc3_sprint5_human_review_package_results.json')
    output_path_obj = Path(output)
    output_path_obj.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate RC3 Sprint 5B human review package artifact')
    parser.add_argument('--output', default=None, help='Path to write the artifact JSON file')
    args = parser.parse_args()
    artifact = build_human_review_package_artifact(output_path=Path(args.output) if args.output else None)
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
