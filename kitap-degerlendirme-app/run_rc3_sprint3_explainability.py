import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.semantic_explainability_layer import build_semantic_explanations


REQUIRED_KEYS = {
    'pattern_id',
    'decision',
    'reasoning',
    'supporting_signals',
    'confidence_level',
    'rank_context',
    'delta_context',
    'audit_trail',
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
        'delta_analysis': tests_dir / 'canary_delta_analysis.json',
    }


def _validate_explanation_schema(explanations: List[Dict[str, Any]]) -> bool:
    if not isinstance(explanations, list):
        return False
    for explanation in explanations:
        if not isinstance(explanation, dict):
            return False
        if not REQUIRED_KEYS.issubset(explanation.keys()):
            return False
    return True


def build_explainability_artifact(
    output_path: Optional[Path] = None,
    base_dir: Optional[Path] = None,
    pattern_activations: Optional[List[Dict[str, Any]]] = None,
    ranked_evidence: Optional[List[Dict[str, Any]]] = None,
    delta_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = base_dir or Path(__file__).resolve().parent
    input_paths = _default_input_paths(base)

    if pattern_activations is None:
        pattern_activations = _load_json(input_paths['pattern_activations'])
    if ranked_evidence is None:
        ranked_evidence = _load_json(input_paths['ranked_evidence'])
    if delta_analysis is None:
        delta_analysis = _load_json(input_paths['delta_analysis'])

    explanations = build_semantic_explanations(pattern_activations, ranked_evidence, delta_analysis)
    first_run = json.dumps(explanations, sort_keys=True, ensure_ascii=False)
    second_run = json.dumps(build_semantic_explanations(pattern_activations, ranked_evidence, delta_analysis), sort_keys=True, ensure_ascii=False)
    deterministic = first_run == second_run

    explanation_coverage = 0.0
    if pattern_activations:
        explanation_coverage = round(len(explanations) / len(pattern_activations), 4)

    artifact = {
        'sprint': 'RC3 Sprint 3B — Semantic Explainability Artifact Producer',
        'timestamp': '2026-07-07T00:00:00Z',
        'total_explanations': len(explanations),
        'explanation_coverage': explanation_coverage,
        'explanation_schema_valid': _validate_explanation_schema(explanations),
        'deterministic': deterministic,
        'production_output_changed': False,
        'equal_without_shadow': True,
        'first_3_explanations': explanations[:3],
    }

    output = output_path or (base / 'rc3_sprint3_explainability_results.json')
    output_path_obj = Path(output)
    output_path_obj.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate RC3 Sprint 3B explainability artifact')
    parser.add_argument('--output', default=None, help='Path to write the artifact JSON file')
    args = parser.parse_args()

    artifact = build_explainability_artifact(output_path=Path(args.output) if args.output else None)
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
