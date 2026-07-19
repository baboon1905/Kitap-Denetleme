import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from runtime_v7.evidence_synthesizer_tracer import EvidenceSynthesizerTracer


def _collect_runtime_files(root: Path) -> List[Path]:
    files = list(root.glob('runtime_*.json'))
    files += list(root.rglob('runtime_*.json'))
    uniq = sorted({p.resolve(): p for p in files}.values(), key=lambda p: str(p))
    return uniq


def _load_summary_ir_from_file(p: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(p.read_text(encoding='utf-8-sig') or '{}')
    except Exception:
        payload = {}
    summary_ir = payload.get('canonical_summary_ir') or payload.get('summary_ir') or payload.get('analiz_sonucu') or payload
    return summary_ir if isinstance(summary_ir, dict) else {}


def process_all(output_path: Path = None) -> Dict[str, Any]:
    root = Path(__file__).resolve().parent
    runtime_files = _collect_runtime_files(root)

    tracer = EvidenceSynthesizerTracer()

    report = {
        'sprint': 'RC4 Sprint 8B — Evidence Synthesis Root Cause',
        'generated_at': None,
        'total_runtime_payloads': len(runtime_files),
        'processed_payloads': 0,
        'per_payload': [],
        'aggregate': {
            'total_input_evidence': 0,
            'total_output_evidence': 0,
            'loss_per_stage': {},
            'removal_reasons': {},
        },
        'shadow_only': True,
    }

    for p in runtime_files:
        summary_ir = _load_summary_ir_from_file(p)
        evidence_snippets = summary_ir.get('evidence_snippets') or {}

        trace_map = tracer.trace_snippets_map(evidence_snippets)
        summary = tracer.summarize_trace(trace_map)

        # Merge into aggregate
        report['aggregate']['total_input_evidence'] += summary.get('total_input_evidence', 0)
        report['aggregate']['total_output_evidence'] += summary.get('total_output_evidence', 0)
        for k, v in (summary.get('loss_per_stage') or {}).items():
            report['aggregate']['loss_per_stage'][k] = report['aggregate']['loss_per_stage'].get(k, 0) + v
        for k, v in (summary.get('removal_reasons') or {}).items():
            report['aggregate']['removal_reasons'][k] = report['aggregate']['removal_reasons'].get(k, 0) + v

        report['per_payload'].append({
            'payload_file': str(p.relative_to(root)),
            'book_title': str(summary_ir.get('title') or p.stem),
            'trace': trace_map,
            'summary': summary,
        })

        report['processed_payloads'] += 1

    # choose first major loss stage and dominant root cause from aggregate
    agg_loss = report['aggregate']['loss_per_stage']
    agg_reasons = report['aggregate']['removal_reasons']
    report['aggregate']['first_stage_with_major_loss'] = max(agg_loss.items(), key=lambda kv: kv[1])[0] if agg_loss else None
    report['aggregate']['dominant_root_cause'] = max(agg_reasons.items(), key=lambda kv: kv[1])[0] if agg_reasons else None

    outp = output_path or root / 'rc4_sprint8b_synthesis_root_cause.json'
    outp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
    return report


if __name__ == '__main__':
    rpt = process_all()
    print('Wrote rc4_sprint8b_synthesis_root_cause.json')
