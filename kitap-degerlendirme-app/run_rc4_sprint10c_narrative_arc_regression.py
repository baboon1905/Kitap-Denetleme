"""RC4 Sprint 10C: Narrative Arc Compression Regression.

Builds narrative arcs from the reconstructed event list produced in Sprint 9B.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from runtime_v7.event_graph_builder import build_event_graph


def load_reconstruction_artifact() -> Dict[str, Any]:
    artifact_path = Path('rc4_sprint9b_event_reconstruction_results.json')
    with open(artifact_path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def _extract_events(book_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    reconstructed_events = book_result.get('reconstructed_events', [])
    if isinstance(reconstructed_events, list):
        return [event for event in reconstructed_events if isinstance(event, dict)]
    return []


def _build_book_result(book_idx: int, book_result: Dict[str, Any]) -> Dict[str, Any]:
    events = _extract_events(book_result)
    graph_result = build_event_graph(events)
    arcs = graph_result.get('arcs', [])

    supporting_counts = [len(arc.get('supporting_events', [])) for arc in arcs]
    average_supporting_events = round(sum(supporting_counts) / len(supporting_counts), 3) if supporting_counts else 0.0
    average_arc_length = round(sum(len(arc.get('progression', [])) for arc in arcs) / len(arcs), 3) if arcs else 0.0

    return {
        'book_idx': book_idx,
        'book_title': book_result.get('book_title') or f'Book {book_idx}',
        'event_count': len(events),
        'arc_count': len(arcs),
        'compression_ratio': round((1 - (len(arcs) / len(events))) if events else 0.0, 3),
        'average_supporting_events': average_supporting_events,
        'average_arc_length': average_arc_length,
        'source_trace_preservation': round(
            sum(1 for arc in arcs if arc.get('source_sentence_ids')) / len(arcs), 3
        ) if arcs else 0.0,
        'deterministic': True,
        'first_5_arcs': arcs[:5],
    }


def run_regression() -> Dict[str, Any]:
    artifact = load_reconstruction_artifact()
    books = artifact.get('books', [])
    book_results = []

    for idx, book_result in enumerate(books, 1):
        book_results.append(_build_book_result(idx, book_result))

    aggregate_metrics = {
        'total_books': len(book_results),
        'total_input_events': sum(book['event_count'] for book in book_results),
        'total_arc_count': sum(book['arc_count'] for book in book_results),
        'average_compression_ratio': round(
            sum(book['compression_ratio'] for book in book_results) / len(book_results), 3
        ) if book_results else 0.0,
        'average_groups_per_book': round(
            sum(book['arc_count'] for book in book_results) / len(book_results), 3
        ) if book_results else 0.0,
        'source_trace_preservation': round(
            sum(book['source_trace_preservation'] for book in book_results) / len(book_results), 3
        ) if book_results else 0.0,
        'deterministic': True,
    }

    result = {
        'sprint': 'RC4 Sprint 10C - Narrative Arc Compression Regression',
        'timestamp': datetime.now().isoformat(),
        'source_data': 'rc4_sprint9b_event_reconstruction_results.json',
        'books': book_results,
        'aggregate_metrics': aggregate_metrics,
    }

    output_path = Path('rc4_sprint10c_narrative_arc_results.json')
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write('\n')

    return result


if __name__ == '__main__':
    run_regression()
    print('Wrote rc4_sprint10c_narrative_arc_results.json')
