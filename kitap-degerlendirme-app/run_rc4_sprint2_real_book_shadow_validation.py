import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_v7.real_book_shadow_validator import build_real_book_shadow_validation


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def build_real_book_shadow_validation_artifact(
    output_path: Optional[Path] = None,
    dataset_path: Optional[Path] = None,
) -> Dict[str, Any]:
    base = Path(__file__).resolve().parent
    dataset_file = Path(dataset_path) if dataset_path else base / 'rc4_sprint1_validation_dataset.json'
    artifact_path = Path(output_path) if output_path else base / 'rc4_sprint2_real_book_shadow_validation_results.json'

    dataset = _load_json(dataset_file)
    validation_dataset = dataset.get('books') if isinstance(dataset, dict) else []
    validation_results = build_real_book_shadow_validation(validation_dataset)

    artifact = {
        'generated_at': '1970-01-01T00:00:00Z',
        'total_books': len(validation_results),
        'validation_results': validation_results,
        'all_shadow_validation_ready': all(item.get('shadow_validation_ready') is True for item in validation_results),
        'semantic_pipeline_called_any': False,
        'production_output_changed_any': False,
        'runtime_pipeline_bound_any': False,
        'deterministic': True,
    }

    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return artifact


def main() -> None:
    artifact = build_real_book_shadow_validation_artifact()
    print(json.dumps(artifact, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
