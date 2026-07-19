import json
import os
from pathlib import Path
from typing import List, Dict, Any

from run_rc4_sprint8a_evidence_provenance_trace import build_rc4_sprint8a_evidence_provenance_report


def _collect_runtime_files(root: Path) -> List[Path]:
    files = list(root.glob('runtime_*.json'))
    files += list(root.rglob('runtime_*.json'))
    # dedupe and sort
    uniq = sorted({p.resolve(): p for p in files}.values(), key=lambda p: str(p))
    return uniq


def _count_source_sentence_ids(obj: Any) -> int:
    # recursively count occurrences of 'source_sentence_id'
    if isinstance(obj, dict):
        c = 1 if 'source_sentence_id' in obj and obj.get('source_sentence_id') else 0
        for v in obj.values():
            c += _count_source_sentence_ids(v)
        return c
    if isinstance(obj, list):
        return sum(_count_source_sentence_ids(i) for i in obj)
    return 0


def _safe_len(x: Any) -> int:
    try:
        return len(x)
    except Exception:
        return 0


def process_all(output_path: Path = None) -> Dict[str, Any]:
    root = Path(__file__).resolve().parent
    runtime_files = _collect_runtime_files(root)

    all_report: Dict[str, Any] = {
        'total_runtime_payloads': len(runtime_files),
        'processed_payloads': 0,
        'per_payload_trace': [],
        'missing_evidence_count': 0,
        'summary_sentence_without_source_count': 0,
        'theme_without_source_count': 0,
        'learning_outcome_without_source_count': 0,
        'character_without_source_count': 0,
        'pipeline_stage_loss_summary': {},
        'likely_loss_stage': None,
    }

    stage_losses = {'extraction': 0, 'synthesis': 0, 'builder': 0}

    for f in runtime_files:
        try:
            payload = json.loads(f.read_text(encoding='utf-8-sig') or '{}')
        except Exception:
            payload = {}

        summary_ir = payload.get('canonical_summary_ir') or payload.get('summary_ir') or payload.get('analiz_sonucu') or payload
        book_id = str(summary_ir.get('book_id') if isinstance(summary_ir, dict) else f.stem)
        title = str(summary_ir.get('kitap_adi') or summary_ir.get('title') or f.stem)

        books = [{"book_id": book_id, "title": title, "summary_ir": summary_ir}]
        report = build_rc4_sprint8a_evidence_provenance_report(books)
        book_report = report.get('books', [])[0]

        # raw evidence: count source_sentence_id occurrences in source summary_ir
        raw_source_count = _count_source_sentence_ids(summary_ir)

        # synthesized evidence count (best-effort)
        se = book_report.get('synthesized_evidence', {})
        synth_count = 0
        if isinstance(se, dict):
            # prefer lists inside synthesized_evidence
            for v in se.values():
                if isinstance(v, list):
                    synth_count = max(synth_count, _safe_len(v))
        elif isinstance(se, list):
            synth_count = _safe_len(se)

        # summary sentences
        bo = book_report.get('builder_output', {}) or {}
        summary_sent_count = 0
        if isinstance(bo, dict):
            if 'narrative' in bo and isinstance(bo['narrative'], list):
                summary_sent_count = len(bo['narrative'])
            elif 'sections' in bo and isinstance(bo['sections'], list):
                # sections may be strings or dicts
                ssum = 0
                for sec in bo['sections']:
                    if isinstance(sec, dict) and 'sentences' in sec:
                        ssum += _safe_len(sec.get('sentences', []))
                summary_sent_count = ssum

        # sentences with source: attempt builder_input evidence mapping
        bi = book_report.get('builder_input', {}) or {}
        sentences_with_source = 0
        sentences_without_source = summary_sent_count
        # builder_input may have 'evidence_snippets' or sections with sentences
        if isinstance(bi, dict):
            es = bi.get('evidence_snippets') or []
            if es:
                sentences_with_source = sum(1 for e in es if e.get('source_sentence_id'))
                sentences_without_source = max(0, summary_sent_count - sentences_with_source)
            elif 'sections' in bi and isinstance(bi['sections'], list):
                cnt_with = 0
                cnt_without = 0
                for sec in bi['sections']:
                    if isinstance(sec, dict):
                        for s in sec.get('sentences', []):
                            if s.get('source_sentence_id'):
                                cnt_with += 1
                            else:
                                cnt_without += 1
                if cnt_with + cnt_without > 0:
                    sentences_with_source = cnt_with
                    sentences_without_source = cnt_without

        # themes and learning outcomes and characters: best-effort from summary_ir
        themes = []
        learning_outcomes = []
        characters = []
        if isinstance(summary_ir, dict):
            tema_analizi = summary_ir.get('tema_analizi') or []
            for t in tema_analizi:
                if t.get('tur') == 'kazanım' or t.get('tur') == 'learning_outcome' or 'kazanım' in str(t.get('tur','')):
                    learning_outcomes.append(t)
                else:
                    themes.append(t)
            # characters might be under 'karakterler' or 'karakter_ozeti'
            chars = summary_ir.get('karakterler') or summary_ir.get('karakter_ozeti') or []
            if isinstance(chars, list):
                characters = chars

        themes_with_source = sum(1 for t in themes if _count_source_sentence_ids(t) > 0)
        themes_without = max(0, len(themes) - themes_with_source)
        lo_with_source = sum(1 for t in learning_outcomes if _count_source_sentence_ids(t) > 0)
        lo_without = max(0, len(learning_outcomes) - lo_with_source)
        chars_with_source = sum(1 for c in characters if _count_source_sentence_ids(c) > 0)
        chars_without = max(0, len(characters) - chars_with_source)

        # pipeline stage loss estimation
        extraction = raw_source_count
        synthesis = synth_count
        builder = sentences_with_source
        stage_losses['extraction'] += 0
        stage_losses['synthesis'] += max(0, extraction - synthesis)
        stage_losses['builder'] += max(0, synthesis - builder)

        all_report['per_payload_trace'].append({
            'payload_file': str(f.relative_to(root)),
            'book_title': title,
            'raw_evidence_count': extraction,
            'synthesized_evidence_count': synthesis,
            'summary_sentence_count': summary_sent_count,
            'summary_sentences_with_source': sentences_with_source,
            'summary_sentences_without_source': sentences_without_source,
            'themes_with_source': themes_with_source,
            'themes_without_source': themes_without,
            'learning_outcomes_with_source': lo_with_source,
            'learning_outcomes_without_source': lo_without,
            'characters_with_source': chars_with_source,
            'characters_without_source': chars_without,
        })

        all_report['processed_payloads'] += 1
        all_report['missing_evidence_count'] += 1 if extraction == 0 else 0
        all_report['summary_sentence_without_source_count'] += sentences_without_source
        all_report['theme_without_source_count'] += themes_without
        all_report['learning_outcome_without_source_count'] += lo_without
        all_report['character_without_source_count'] += chars_without

    # pipeline summary
    all_report['pipeline_stage_loss_summary'] = stage_losses
    # likely loss stage is the stage with largest accumulated loss
    likely = max(stage_losses.items(), key=lambda kv: kv[1])[0] if stage_losses else None
    all_report['likely_loss_stage'] = likely

    outp = output_path or root / 'rc4_sprint8a_evidence_provenance_trace_all.json'
    outp.write_text(json.dumps(all_report, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
    return all_report


if __name__ == '__main__':
    report = process_all()
    print('Wrote', 'rc4_sprint8a_evidence_provenance_trace_all.json')
