"""RC4 Sprint 10A: Event Graph Regression Check.

Consumes the Sprint 9B reconstruction artifact and emits a deterministic,
shadow-only event grouping artifact for regression validation.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from runtime_v7.event_graph_builder import build_event_graph


def load_reconstruction_artifact() -> Dict[str, Any]:
    artifact_path = Path('rc4_sprint9b_event_reconstruction_results.json')
    if not artifact_path.exists():
        raise FileNotFoundError(f'Missing artifact: {artifact_path}')

    with open(artifact_path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def _extract_events_from_book(book_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    reconstructed_events = book_result.get('reconstructed_events', [])
    if isinstance(reconstructed_events, list):
        return [event for event in reconstructed_events if isinstance(event, dict)]
    return []


def build_book_result(book_idx: int, book_result: Dict[str, Any]) -> Dict[str, Any]:
    event_payload = _extract_events_from_book(book_result)
    input_event_count = len(event_payload)
    graph_result = build_event_graph(event_payload)
    event_groups = graph_result.get('event_groups', [])

    group_importance_values = [float(group.get('importance', 0.0) or 0.0) for group in event_groups]
    average_group_importance = round(sum(group_importance_values) / len(group_importance_values), 3) if group_importance_values else 0.0
    source_sentence_id_preservation_rate = 0.0
    if event_payload:
        preserved = sum(1 for event in event_payload if event.get('source_sentence_ids'))
        source_sentence_id_preservation_rate = round(preserved / len(event_payload), 3)

    return {
        'book_idx': book_idx,
        'book_title': book_result.get('book_title') or f'Book {book_idx}',
        'input_event_count': input_event_count,
        'event_group_count': len(event_groups),
        'compression_ratio': round((1 - (len(event_groups) / input_event_count)) if input_event_count else 0.0, 3),
        'first_5_event_groups': event_groups[:5],
        'average_group_importance': average_group_importance,
        'source_sentence_id_preservation_rate': source_sentence_id_preservation_rate,
        'production_output_changed': False,
        'runtime_pipeline_bound': False,
    }


def run_regression() -> Dict[str, Any]:
    artifact = load_reconstruction_artifact()
    books = artifact.get('books', [])

    book_results = []
    total_input_events = 0
    total_event_groups = 0
    total_compression_ratio = 0.0

    for idx, book_result in enumerate(books, 1):
        book_summary = build_book_result(idx, book_result)
        book_results.append(book_summary)
        total_input_events += book_summary['input_event_count']
        total_event_groups += book_summary['event_group_count']
        total_compression_ratio += book_summary['compression_ratio']

    aggregate_metrics = {
        'total_books': len(book_results),
        'total_input_events': total_input_events,
        'total_event_groups': total_event_groups,
        'average_compression_ratio': round(total_compression_ratio / len(book_results), 3) if book_results else 0.0,
        'average_groups_per_book': round(total_event_groups / len(book_results), 3) if book_results else 0.0,
        'source_sentence_id_preservation_rate': round(
            sum(book['source_sentence_id_preservation_rate'] for book in book_results) / len(book_results),
            3,
        ) if book_results else 0.0,
        'deterministic': True,
        'production_output_changed_any': False,
        'runtime_pipeline_bound_any': False,
    }

    result = {
        'sprint': 'RC4 Sprint 10A - Event Graph Regression Check',
        'timestamp': datetime.now().isoformat(),
        'source_data': 'rc4_sprint9b_event_reconstruction_results.json',
        'books': book_results,
        'aggregate_metrics': aggregate_metrics,
    }

    output_path = Path('rc4_sprint10a_event_graph_results.json')
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write('\n')

    return result


if __name__ == '__main__':
    run_regression()
    print('Wrote rc4_sprint10a_event_graph_results.json')
