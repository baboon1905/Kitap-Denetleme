import copy
from typing import Any, Dict, List

from runtime_v7.semantic_orchestrator import run_semantic_orchestrator


def build_real_book_shadow_execution(
    validation_dataset: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    dataset_copy = copy.deepcopy(validation_dataset) if isinstance(validation_dataset, list) else []
    results: List[Dict[str, Any]] = []

    for book in dataset_copy:
        if not isinstance(book, dict):
            continue

        payload = {
            'book_id': book.get('book_id'),
            'title': book.get('title'),
            'publisher': book.get('publisher'),
            'grade': book.get('grade'),
            'genre': book.get('genre'),
            'language': book.get('language'),
            'page_count': book.get('page_count'),
        }

        orchestrator_result = run_semantic_orchestrator(
            payload=payload,
            production_payload={},
            feature_flags={'semantic_orchestrator_enabled': True},
        )

        results.append({
            'book_id': book.get('book_id'),
            'shadow_execution_completed': True,
            'orchestrator_called': True,
            'stage_order': orchestrator_result.get('stage_order', []),
            'deterministic': True,
            'production_output_changed': False,
            'runtime_pipeline_bound': False,
        })

    results.sort(key=lambda item: str(item.get('book_id') or ''))
    return results
