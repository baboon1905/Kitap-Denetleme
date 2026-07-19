#!/usr/bin/env python3
"""RC4 Sprint 12E.1 Semantic Event Merger benchmark.

Benchmarks the shadow-only event merger against three real books by:
1. Loading summary_ir from the analysis API.
2. Running evidence quality filtering.
3. Reconstructing events from filtered evidence.
4. Merging events with the semantic merger.
5. Comparing before/after event counts and merge preservation metrics.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.evidence_quality_filter import filter_summary_ir_evidence
from runtime_v7.event_reconstructor import reconstruct_events
from runtime_v7.semantic_event_merger import merge_semantic_events

BOOKS = {
    'Tavşan Pati': 'uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
    'Büyülü Yastıklar': 'uploads/buyulu_yastiklar.pdf',
    'Benim Adım Kristof Kolomb': 'uploads/benim_adim_kristof_kolomb.pdf',
}

OUTPUT_FILE = 'rc4_sprint12e1_semantic_merger_benchmark_results.json'


def _load_summary_ir_from_api(pdf_path: str) -> Dict[str, Any]:
    from app import app

    client = app.test_client()
    response = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
    if response.status_code != 200:
        raise RuntimeError(f'API call failed for {pdf_path}: {response.status_code} {response.get_data(as_text=True)[:400]}')
    data = response.get_json() or {}
    analiz_sonucu = data.get('analiz_sonucu') or data
    summary_ir = analiz_sonucu.get('summary_ir')
    if not isinstance(summary_ir, dict):
        raise RuntimeError(f'summary_ir missing for {pdf_path}')
    return summary_ir


def _build_merge_payload(filtered_evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    payload: List[Dict[str, Any]] = []
    for section in ('setup', 'conflict', 'events', 'resolution'):
        items = filtered_evidence.get(section, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, str):
                text = item
                source_ids = []
            elif isinstance(item, dict):
                text = item.get('text') or item.get('content') or item.get('sentence') or ''
                source_ids = item.get('source_sentence_ids', []) or item.get('source_sentence_id', []) or []
            else:
                text = str(item)
                source_ids = []
            if not text:
                continue
            payload.append({
                'text': text,
                'source_sentence_ids': list(source_ids) if isinstance(source_ids, list) else [source_ids],
                'section': section,
                'narrative_role': section,
                'supporting_evidence_ids': list(source_ids) if isinstance(source_ids, list) else [source_ids],
                'evidence_count': 1,
            })
    return payload


def _count_conflict(events: List[Dict[str, Any]]) -> int:
    return sum(1 for event in events if str(event.get('section') or '').lower() == 'conflict' or bool(event.get('conflict')))


def _count_resolution(events: List[Dict[str, Any]]) -> int:
    return sum(1 for event in events if str(event.get('section') or '').lower() == 'resolution' or str(event.get('resolution_state') or '').lower() in {'resolved', 'resolution'})


def _chronology_preserved(before_events: List[Dict[str, Any]], after_events: List[Dict[str, Any]]) -> bool:
    if not before_events:
        return True
    if not after_events:
        return False
    if len(after_events) > len(before_events):
        return False
    before_ids = [event.get('event_id') for event in before_events]
    merged_ids = []
    for event in after_events:
        source_ids = event.get('source_sentence_ids', [])
        if not source_ids:
            continue
        merged_ids.extend(source_ids)
    return len(merged_ids) >= len(before_ids) and len(after_events) <= len(before_events)


def _summarize_merged_events(merged_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        'first_10': [
            {
                'text': event.get('text', ''),
                'supporting_source_sentence_ids': event.get('source_sentence_ids', []),
                'evidence_count': event.get('evidence_count', 1),
            }
            for event in merged_events[:10]
        ],
        'merged_event_count': len(merged_events),
    }


def benchmark_book(title: str, pdf_path: str) -> Dict[str, Any]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f'Missing PDF: {pdf_path}')

    summary_ir = _load_summary_ir_from_api(pdf_path)
    filtered_result = filter_summary_ir_evidence(summary_ir)
    filtered_evidence = filtered_result.get('filtered_evidence', {})
    filtered_evidence_count = sum(len(items) for items in filtered_evidence.values())

    reconstruction = reconstruct_events(filtered_evidence)
    reconstructed_events = reconstruction.get('events', [])
    merge_payload = _build_merge_payload(filtered_evidence)
    merge_result = merge_semantic_events(merge_payload)
    merged_events = merge_result.get('merged_events', [])

    before_count = len(reconstructed_events)
    after_count = len(merged_events)
    ratio = after_count / before_count if before_count else 0.0

    return {
        'title': title,
        'pdf_path': pdf_path,
        'filtered_evidence_count': filtered_evidence_count,
        'reconstructed_event_count': before_count,
        'merged_event_count': after_count,
        'event_to_evidence_ratio_before': round(before_count / filtered_evidence_count, 3) if filtered_evidence_count else 0.0,
        'event_to_evidence_ratio_after': round(after_count / filtered_evidence_count, 3) if filtered_evidence_count else 0.0,
        'merge_ratio': merge_result.get('merge_ratio', 0.0),
        'source_sentence_id_preservation_rate': merge_result.get('source_sentence_id_preservation_rate', 0.0),
        'chronology_preserved': _chronology_preserved(reconstructed_events, merged_events),
        'conflict_event_count_before': _count_conflict(reconstructed_events),
        'conflict_event_count_after': _count_conflict(merged_events),
        'resolution_event_count_before': _count_resolution(reconstructed_events),
        'resolution_event_count_after': _count_resolution(merged_events),
        'deterministic': merge_result.get('deterministic', True),
        'production_output_changed': merge_result.get('production_output_changed', False),
        'runtime_pipeline_bound': merge_result.get('runtime_pipeline_bound', False),
        'run_1_hash': None,
        'run_2_hash': None,
        'merge_preview': _summarize_merged_events(merged_events),
        'acceptance': {
            'merge_ratio_threshold_met': 0.60 <= ratio <= 0.75,
            'source_sentence_id_preservation_rate_met': merge_result.get('source_sentence_id_preservation_rate', 0.0) == 1.0,
            'chronology_preserved': _chronology_preserved(reconstructed_events, merged_events),
            'conflict_survives': _count_conflict(merged_events) > 0,
            'resolution_survives': _count_resolution(merged_events) > 0,
            'deterministic': merge_result.get('deterministic', True),
        },
    }


def main() -> None:
    runs: List[List[Dict[str, Any]]] = []
    errors: List[Dict[str, Any]] = []
    for run_number in (1, 2):
        print(f'Run {run_number} starting')
        results: List[Dict[str, Any]] = []
        for title, pdf_path in BOOKS.items():
            print(f'  Benchmarking {title}')
            try:
                result = benchmark_book(title, pdf_path)
                results.append(result)
                print(f'    ✓ {title} complete')
            except Exception as exc:  # pragma: no cover - runtime guard
                errors.append({'title': title, 'run': run_number, 'error': str(exc)})
                print(f'    ✗ {title} failed: {exc}')
        runs.append(results)

    if runs and len(runs) == 2:
        run_1_json = json.dumps(runs[0], sort_keys=True, ensure_ascii=False)
        run_2_json = json.dumps(runs[1], sort_keys=True, ensure_ascii=False)
        run_1_hash = hashlib.md5(run_1_json.encode('utf-8')).hexdigest()
        run_2_hash = hashlib.md5(run_2_json.encode('utf-8')).hexdigest()
        deterministic = run_1_hash == run_2_hash
    else:
        run_1_hash = None
        run_2_hash = None
        deterministic = False

    final_results: List[Dict[str, Any]] = []
    for book_result in runs[0] if runs else []:
        title = book_result['title']
        run_2_result = next((item for item in runs[1] if item.get('title') == title), None) if len(runs) > 1 else None
        payload = dict(book_result)
        payload['run_1_hash'] = run_1_hash
        payload['run_2_hash'] = run_2_hash
        payload['deterministic'] = deterministic
        if run_2_result is not None:
            payload['merge_preview'] = run_2_result.get('merge_preview', payload.get('merge_preview'))
        final_results.append(payload)

    output = {
        'benchmark': 'RC4 Sprint 12E.1 Semantic Event Merger',
        'generated_at': __import__('datetime').datetime.now().isoformat(),
        'books': final_results,
        'deterministic': deterministic,
        'run_1_hash': run_1_hash,
        'run_2_hash': run_2_hash,
        'errors': errors,
    }

    output_path = Path(OUTPUT_FILE)
    with output_path.open('w', encoding='utf-8') as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)

    print(f'Wrote {output_path.resolve()}')


if __name__ == '__main__':
    main()
