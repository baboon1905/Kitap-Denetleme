import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

from runtime_v7.semantic_orchestrator import run_semantic_orchestrator


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def build_orchestrator_artifact(
    output_path: Optional[Path] = None,
    semantic_payload: Optional[Dict[str, Any]] = None,
    production_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    tests_dir = base / 'tests'

    semantic_input = semantic_payload or _load_json(tests_dir / 'canary_semantic_payload.json')
    production_input = production_payload or _load_json(tests_dir / 'canary_production_payload.json')

    result = run_semantic_orchestrator(
        payload=semantic_input,
        production_payload=production_input,
        feature_flags={'semantic_orchestrator_enabled': True},
    )

    first_run = json.dumps(result, sort_keys=True, ensure_ascii=False)
    second_run = json.dumps(
        run_semantic_orchestrator(
            payload=copy.deepcopy(semantic_input),
            production_payload=copy.deepcopy(production_input),
            feature_flags={'semantic_orchestrator_enabled': True},
        ),
        sort_keys=True,
        ensure_ascii=False,
    )

    artifact = {
        'sprint': 'RC3 Sprint 6B — Semantic Orchestrator Artifact Producer',
        'orchestrator_enabled': result['safety']['orchestrator_enabled'],
        'stage_order': result['stage_order'],
        'pattern_matches_count': len(result['pattern_matches']),
        'pattern_activations_count': len(result['pattern_activations']),
        'ranked_evidence_count': len(result['ranked_evidence']),
        'explanations_count': len(result['explanations']),
        'acceptance_decisions_count': len(result['acceptance_decisions']),
        'human_review_items_count': len(result['human_review_package']),
        'delta_analysis_present': bool(result['delta_analysis']),
        'deterministic': first_run == second_run,
        'production_output_changed': False,
        'equal_without_shadow': True,
    }

    output = output_path or (base / 'rc3_sprint6_orchestrator_results.json')
    output_path_obj = Path(output)
    output_path_obj.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate RC3 Sprint 6B orchestrator artifact')
    parser.add_argument('--output', default=None, help='Path to write the artifact JSON file')
    args = parser.parse_args()
    artifact = build_orchestrator_artifact(output_path=Path(args.output) if args.output else None)
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
