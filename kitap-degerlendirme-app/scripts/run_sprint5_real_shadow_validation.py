#!/usr/bin/env python3
"""
Run Sprint 5: Real Shadow Validation

Collect real shadow payloads from the Flask app (shadow-only mode), extract pattern-match entries,
and run the semantic pattern monitor to produce Sprint 5 artifacts.

Usage: python run_sprint5_real_shadow_validation.py [--count N]
"""
import io
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import app as flask_app_module

from runtime_v7 import semantic_pattern_monitor


def _find_matches(obj: Any) -> Optional[List[Dict[str, Any]]]:
    """Recursively search for a list of candidate match dicts in the shadow payload.
    A candidate list is where each item is a dict and at least one item contains keys
    that look like a pattern match (pattern id/name and some confidence/recommendation).
    """
    if isinstance(obj, dict):
        for v in obj.values():
            res = _find_matches(v)
            if res:
                return res
        return None
    if isinstance(obj, list) and obj:
        # check if list of dict-like match objects
        if all(isinstance(i, dict) for i in obj):
            sample = obj[0]
            keyset = set(sample.keys())
            trigger_keys = {'pattern_id', 'id', 'pattern', 'raw_confidence', 'calibrated_confidence', 'recommendation'}
            if keyset & trigger_keys:
                return obj
        # otherwise recurse into list items
        for item in obj:
            res = _find_matches(item)
            if res:
                return res
    return None


def _normalize_match(m: Dict[str, Any]) -> Dict[str, Any]:
    # Map common possible keys to monitor expected shape
    pid = m.get('pattern_id') or m.get('id') or m.get('pattern') or m.get('name')
    raw = m.get('raw_confidence') or m.get('raw') or m.get('raw_conf') or 0.0
    calib = m.get('calibrated_confidence') or m.get('calibrated') or m.get('calibrated_confidence') or raw
    is_fp = bool(m.get('is_fp') or m.get('false_positive') or m.get('fp'))
    rec = m.get('recommendation') or m.get('recommendation_reason') or None

    return {
        'pattern_id': pid,
        'raw_confidence': float(raw) if raw is not None else 0.0,
        'calibrated_confidence': float(calib) if calib is not None else float(raw or 0.0),
        'is_fp': is_fp,
        'recommendation': rec,
    }


def _load_library() -> List[Dict[str, Any]]:
    base = Path(__file__).resolve().parent.parent
    candidates = [base / 'rc2_sprint3_semantic_pattern_library.json', base.parent / 'rc2_sprint3_semantic_pattern_library.json']
    for p in candidates:
        if p.exists():
            with open(p, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                # expect list under 'patterns' or top-level list
                if isinstance(data, dict) and 'patterns' in data:
                    return data['patterns']
                if isinstance(data, list):
                    return data
    raise FileNotFoundError('rc2_sprint3_semantic_pattern_library.json not found in expected locations')


def run(count: int = 10):
    client = flask_app_module.app.test_client()
    uploads_dir = Path(os.path.dirname(flask_app_module.__file__)) / 'uploads'
    files = sorted([p for p in uploads_dir.iterdir() if p.is_file()])[:count]
    if not files:
        print('No upload files found in', uploads_dir)
        return

    patterns = _load_library()
    all_matches: List[Dict[str, Any]] = []
    processed = 0

    for f in files:
        pdf_path = str(f.resolve())
        resp_analiz = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
        if resp_analiz.status_code != 200:
            print('analiz failed for', pdf_path, 'status', resp_analiz.status_code)
            continue
        analiz_json = resp_analiz.get_json() or {}
        analiz_sonucu = analiz_json.get('analiz_sonucu') or {}

        def fake_pdf(payload):
            fake_pdf.captured = dict(payload or {})
            return io.BytesIO(b"%PDF-1.4\n%fake-pdf\n")

        os.environ['V7_SHADOW_MODE'] = 'true'
        os.environ['V7_NARRATIVE_GRAPH'] = 'true'
        fake_pdf.captured = None
        with patch.object(flask_app_module, 'build_theme_pdf_report', side_effect=fake_pdf):
            client.post('/api/tema-kazanim/rapor', json={'analiz_sonucu': analiz_sonucu, 'format': 'pdf'})
        captured = getattr(fake_pdf, 'captured', {}) or {}
        true_shadow = captured.get('_runtime_v7_shadow') or {}
        narrative = true_shadow.get('narrative') if isinstance(true_shadow, dict) else None

        matches = None
        # Try common locations
        if isinstance(narrative, dict):
            matches = _find_matches(narrative) or _find_matches(true_shadow)
        else:
            matches = _find_matches(true_shadow) or _find_matches(captured)

        if not matches:
            print(f'No match-like structures found in shadow for {f.name} — skipping')
            continue

        # Normalize and collect matches
        for m in matches:
            nm = _normalize_match(m)
            if nm.get('pattern_id'):
                all_matches.append(nm)

        processed += 1

    if processed == 0:
        print('No valid shadow matches extracted — aborting')
        return

    # Run monitoring twice to check determinism
    out1 = semantic_pattern_monitor.run_monitoring(patterns, all_matches, total_docs=processed, output_prefix='rc2_sprint5_real_shadow')
    out2 = semantic_pattern_monitor.run_monitoring(patterns, all_matches, total_docs=processed, output_prefix='rc2_sprint5_real_shadow_det2')

    # Save determinism comparison
    det_path = Path(__file__).resolve().parent.parent / 'rc2_sprint5_real_shadow_determinism.json'
    det = {
        'patterns_equal': out1['pattern_metrics'] == out2['pattern_metrics'],
        'gates_equal': out1['quality_gates'] == out2['quality_gates'],
        'library_metrics_equal': out1['library_metrics'] == out2['library_metrics'],
    }
    with open(det_path, 'w', encoding='utf-8') as fh:
        json.dump(det, fh, ensure_ascii=False, indent=2)

    print('Processed', processed, 'books')
    print('Artifacts written:')
    for k, v in out1['artifact_files'].items():
        print('-', k, ':', v)
    print('-', 'determinism:', det_path)


if __name__ == '__main__':
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except Exception:
            print('usage: python run_sprint5_real_shadow_validation.py [count]')
            sys.exit(2)
    run(count=count)
