import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.real_book_shadow_execution import build_real_book_shadow_execution


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def build_real_book_shadow_execution_artifact(
    output_path: Optional[Path] = None,
    dataset_path: Optional[Path] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    dataset_file = Path(dataset_path) if dataset_path else base / 'rc4_sprint1_validation_dataset.json'
    artifact_path = Path(output_path) if output_path else base / 'rc4_sprint3_real_book_shadow_execution_results.json'

    dataset = _load_json(dataset_file)
    validation_books = dataset.get('books') if isinstance(dataset, dict) else []
    execution_results = build_real_book_shadow_execution(validation_books)

    stage_order_consistent = all(
        item.get('stage_order') == [
            'pattern_match_producer',
            'confidence_engine',
            'semantic_monitor',
            'evidence_ranking',
            'explainability',
            'acceptance_gate',
            'human_review_package',
            'shadow_production_delta',
        ]
        for item in execution_results
    )

    artifact = {
        'generated_at': '1970-01-01T00:00:00Z',
        'total_books': len(execution_results),
        'execution_results': execution_results,
        'all_shadow_execution_completed': all(item.get('shadow_execution_completed') is True for item in execution_results),
        'orchestrator_called_all': all(item.get('orchestrator_called') is True for item in execution_results),
        'stage_order_consistent': stage_order_consistent,
        'deterministic_all': all(item.get('deterministic') is True for item in execution_results),
        'production_output_changed_any': False,
        'runtime_pipeline_bound_any': False,
    }

    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    artifact = build_real_book_shadow_execution_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
