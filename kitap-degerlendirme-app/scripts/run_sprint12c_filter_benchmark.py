#!/usr/bin/env python3
"""
RC4 Sprint 12C - Evidence Quality Filter Benchmark
"""

import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime_v7.evidence_quality_filter import filter_summary_ir_evidence

BOOKS = {
    'Tavşan Pati': 'uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
    'Büyülü Yastıklar': 'uploads/buyulu_yastiklar.pdf',
    'Benim Adım Kristof Kolomb': 'uploads/benim_adim_kristof_kolomb.pdf',
}

OUTPUT_FILE = 'rc4_sprint12d_ocr_aware_filter_benchmark_results.json'


def load_summary_ir_from_api(pdf_path: str):
    from app import app

    client = app.test_client()
    payload = {'dosya_yolu': pdf_path}
    response = client.post('/api/tema-kazanim/analiz', json=payload)
    if response.status_code != 200:
        raise RuntimeError(f'API call failed for {pdf_path}: {response.status_code}')
    data = response.get_json() or {}
    analiz_sonucu = data.get('analiz_sonucu') or data
    summary_ir = analiz_sonucu.get('summary_ir')
    if not isinstance(summary_ir, dict):
        raise RuntimeError(f'summary_ir missing or invalid for {pdf_path}')
    return summary_ir


def benchmark_book(title: str, pdf_path: str):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f'Missing PDF: {pdf_path}')

    summary_ir = load_summary_ir_from_api(pdf_path)
    result = filter_summary_ir_evidence(summary_ir)

    section_input_counts = result['metrics'].get('section_input_counts', {})
    section_output_counts = {section: len(result['filtered_evidence'].get(section, [])) for section in section_input_counts}
    source_ids_ok = True
    for section, items in result['filtered_evidence'].items():
        for item in items:
            if not isinstance(item.get('source_sentence_ids'), list):
                source_ids_ok = False
            if item.get('source_sentence_ids') and not all(isinstance(i, str) for i in item['source_sentence_ids']):
                source_ids_ok = False

    return {
        'title': title,
        'pdf_path': pdf_path,
        'summary_ir_keys': list(summary_ir.keys()),
        'section_input_counts': section_input_counts,
        'section_output_counts': section_output_counts,
        'section_retention_rates': result['metrics'].get('section_retention_rates', {}),
        'section_available_counts': result['metrics'].get('section_available_counts', {}),
        'section_retention_shortfall_counts': result['metrics'].get('section_retention_shortfall_counts', {}),
        'section_retention_shortfall_reasons': result['metrics'].get('section_retention_shortfall_reasons', {}),
        'input_count': result['metrics']['input_count'],
        'output_count': result['metrics']['output_count'],
        'reduction_rate': result['metrics']['reduction_rate'],
        'noise_removed': result['metrics']['noise_removed'],
        'low_quality_removed': result['metrics'].get('low_quality_removed', 0),
        'duplicates_removed': result['metrics']['duplicates_removed'],
        'mandatory_preserved_count': result['metrics'].get('mandatory_preserved_count', 0),
        'avg_semantic_score_before': result['metrics'].get('avg_semantic_score_before', 0.0),
        'avg_semantic_score_after': result['metrics'].get('avg_semantic_score_after', 0.0),
        'avg_ocr_quality_score_before': result['metrics'].get('avg_ocr_quality_score_before', 0.0),
        'avg_ocr_quality_score_after': result['metrics'].get('avg_ocr_quality_score_after', 0.0),
        'avg_final_quality_score_before': result['metrics'].get('avg_final_quality_score_before', 0.0),
        'avg_final_quality_score_after': result['metrics'].get('avg_final_quality_score_after', 0.0),
        'retention_shortfall_count': result['metrics'].get('retention_shortfall_count', 0),
        'retention_shortfall_reason': result['metrics'].get('retention_shortfall_reason', ''),
        'quality_threshold_used': result['metrics'].get('quality_threshold_used', {}),
        'source_sentence_ids_preserved': source_ids_ok,
    }


def main():
    runs = []
    errors = []

    for run_number in (1, 2):
        print(f'Benchmark run {run_number}')
        results = []
        for title, pdf_path in BOOKS.items():
            print(f'Benchmarking {title}')
            try:
                result = benchmark_book(title, pdf_path)
                results.append(result)
                print(f'  ✓ {title} complete')
            except Exception as exc:
                errors.append({'title': title, 'run': run_number, 'error': str(exc)})
                print(f'  ✗ {title} failed: {exc}')
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

    output = {
        'benchmark': 'RC4 Sprint 12D OCR Aware Evidence Quality Filter',
        'results': runs[0] if runs else [],
        'deterministic': deterministic,
        'run_1_hash': run_1_hash,
        'run_2_hash': run_2_hash,
        'errors': errors,
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print('\nBenchmark completed')
    print(f'Wrote {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
