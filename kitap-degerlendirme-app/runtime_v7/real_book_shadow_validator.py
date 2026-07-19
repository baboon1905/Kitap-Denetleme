import copy
from typing import Any, Dict, List


def build_real_book_shadow_validation(
    validation_dataset: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    dataset_copy = copy.deepcopy(validation_dataset) if isinstance(validation_dataset, list) else []
    results: List[Dict[str, Any]] = []

    for book in dataset_copy:
        if not isinstance(book, dict):
            continue
        results.append({
            'book_id': book.get('book_id'),
            'validation_status': 'pending',
            'shadow_validation_ready': True,
            'semantic_pipeline_called': False,
            'production_output_changed': False,
            'runtime_pipeline_bound': False,
        })

    results.sort(key=lambda item: str(item.get('book_id') or ''))
    return results
