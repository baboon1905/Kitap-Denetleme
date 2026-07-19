import os
import json
import random
import sys
import io
from pathlib import Path

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure project root import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from runtime_v7.event_reconstructor import reconstruct_events

# Mapping of human book names to upload paths (same as benchmark snapshot)
BOOKS = {
    'Tavşan Pati': 'uploads/arkadaslik_oykuleri_tavsan_patinin_sasirtici_yolculugu_ic.pdf',
    'Büyülü Yastıklar': 'uploads/buyulu_yastiklar.pdf',
    'Benim Adım Kristof Kolomb': 'uploads/benim_adim_kristof_kolomb.pdf',
}

OUTPUT = {
    'sprint': 'RC4 Sprint 11B - Event Reconstructor on real books',
    'timestamp': __import__('datetime').datetime.now().isoformat(),
    'books': {}
}

client = flask_app.test_client()

for book_name, pdf_rel in BOOKS.items():
    pdf_path = os.path.abspath(pdf_rel)
    print(f"Processing {book_name} -> {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"  ⚠ Missing PDF: {pdf_path}")
        OUTPUT['books'][book_name] = {'error': 'missing_pdf', 'path': pdf_path}
        continue

    # Call analysis endpoint to get extracted evidence
    resp = client.post('/api/tema-kazanim/analiz', json={'dosya_yolu': pdf_path})
    if resp.status_code != 200:
        print(f"  ✗ Analysis failed: {resp.status_code}")
        OUTPUT['books'][book_name] = {'error': 'analysis_failed', 'status': resp.status_code}
        continue

    payload = resp.get_json() or {}
    analiz_sonucu = payload.get('analiz_sonucu') or payload.get('analysis_result') or payload

    # Try to find summary_ir style evidence
    summary_ir = analiz_sonucu.get('summary_ir') if isinstance(analiz_sonucu, dict) else None
    evidence_snippets = {'setup': [], 'conflict': [], 'events': [], 'resolution': []}

    # Helper to normalize section names
    def normalize_section(label):
        if not label:
            return 'events'
        l = label.lower()
        if 'setup' in l or 'başlangıç' in l or 'setup' in l:
            return 'setup'
        if 'conflict' in l or 'çatış' in l or 'gelişme' in l:
            return 'conflict'
        if 'resolution' in l or 'sonuç' in l:
            return 'resolution'
        if 'olay' in l or 'event' in l:
            return 'events'
        return 'events'

    # Extract characters/themes
    characters = []
    themes = []
    if isinstance(summary_ir, dict):
        characters = summary_ir.get('central_entities') or summary_ir.get('characters') or []
        themes = summary_ir.get('themes') or []
        # Primary: evidence_snippets
        ev = summary_ir.get('evidence_snippets')
        if isinstance(ev, dict):
            for sec in ['setup', 'conflict', 'events', 'resolution']:
                items = ev.get(sec) or []
                for it in items:
                    if isinstance(it, dict):
                        text = it.get('text') or it.get('alinti') or it.get('ana_metni')
                    else:
                        text = it
                    if text:
                        evidence_snippets[sec].append(text)
        # Raw extracted fallback
        raw = summary_ir.get('__raw_extracted__') or []
        for item in raw:
            if isinstance(item, dict):
                text = item.get('text')
                raw_meta = item.get('raw') or {}
                section_label = raw_meta.get('olay_bolumu') or raw_meta.get('event_section') or ''
                sec = normalize_section(section_label)
                if text:
                    evidence_snippets[sec].append(text)

    # Generic fallback: look inside analiz_sonucu for evidence-like lists
    if not any(evidence_snippets.values()):
        for key in ('evidence', 'evidence_snippets', 'extracted_evidence'):
            candidate = analiz_sonucu.get(key) if isinstance(analiz_sonucu, dict) else None
            if isinstance(candidate, dict):
                for sec, items in candidate.items():
                    sec_norm = normalize_section(sec)
                    for it in items or []:
                        if isinstance(it, dict):
                            text = it.get('text') or it.get('alinti')
                        else:
                            text = it
                        if text:
                            evidence_snippets[sec_norm].append(text)
            elif isinstance(candidate, list):
                for it in candidate:
                    if isinstance(it, dict):
                        text = it.get('text')
                    else:
                        text = it
                    if text:
                        evidence_snippets['events'].append(text)

    # Final fallback: try to gather sentences from canonical_summary_ir if present
    if not any(evidence_snippets.values()):
        cs = analiz_sonucu.get('canonical_summary_ir') if isinstance(analiz_sonucu, dict) else None
        if isinstance(cs, dict):
            snippets = cs.get('evidence_snippets') or cs.get('evidence') or []
            for it in snippets:
                if isinstance(it, dict):
                    text = it.get('text')
                else:
                    text = it
                if text:
                    evidence_snippets['events'].append(text)

    # If still empty, try a recursive sweep of the analysis payload
    # to find any nodes that contain 'metin', 'alinti' or 'text' fields.
    def recursive_collect(obj):
        found = []
        if isinstance(obj, dict):
            text = None
            if 'metin' in obj and isinstance(obj.get('metin'), str):
                text = obj.get('metin')
            elif 'alinti' in obj and isinstance(obj.get('alinti'), str):
                text = obj.get('alinti')
            elif 'text' in obj and isinstance(obj.get('text'), str):
                text = obj.get('text')

            section_label = obj.get('olay_bolumu') or obj.get('event_section') or ''
            if text:
                found.append((text, section_label))

            for v in obj.values():
                found.extend(recursive_collect(v))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(recursive_collect(item))
        return found

    total_snippets = sum(len(v) for v in evidence_snippets.values())
    if total_snippets == 0:
        collected = recursive_collect(analiz_sonucu)
        for text, section_label in collected:
            sec = normalize_section(section_label)
            evidence_snippets[sec].append(text)
        total_snippets = sum(len(v) for v in evidence_snippets.values())

    if total_snippets == 0:
        print(f"  ⚠ No evidence snippets extracted for {book_name}")
        OUTPUT['books'][book_name] = {'error': 'no_evidence_extracted'}
        continue

    # Run event reconstructor
    recon = reconstruct_events(
        evidence_snippets=evidence_snippets,
        characters=characters,
        themes=themes,
        payload_file=os.path.basename(pdf_path),
        book_index=0,
    )

    events = recon.get('events', [])

    # Compute metrics
    total_events = len(events)
    def filled(prop):
        return sum(1 for e in events if e.get(prop))

    metrics = {
        'total_events': total_events,
        'goal_filled': filled('goal'),
        'object_filled': filled('object'),
        'location_filled': filled('location_or_context'),
        'cause_filled': filled('cause'),
        'effect_filled': filled('effect'),
        'goal_fill_rate': round(filled('goal') / total_events, 3) if total_events else 0.0,
        'object_fill_rate': round(filled('object') / total_events, 3) if total_events else 0.0,
        'location_fill_rate': round(filled('location_or_context') / total_events, 3) if total_events else 0.0,
        'cause_fill_rate': round(filled('cause') / total_events, 3) if total_events else 0.0,
        'effect_fill_rate': round(filled('effect') / total_events, 3) if total_events else 0.0,
        'narrative_function_distribution': {},
        'temporal_marker_distribution': {},
        'resolution_state_distribution': {},
    }

    from collections import Counter
    metrics['narrative_function_distribution'] = dict(Counter(e.get('narrative_function') for e in events))
    metrics['temporal_marker_distribution'] = dict(Counter(e.get('temporal_marker') for e in events))
    metrics['resolution_state_distribution'] = dict(Counter(e.get('resolution_state') for e in events))

    # Sample 10 random enriched events (without full supporting evidence to reduce size)
    sample_count = min(10, len(events))
    sampled = random.sample(events, sample_count) if sample_count else []

    OUTPUT['books'][book_name] = {
        'pdf_path': pdf_path,
        'input_evidence_count': total_snippets,
        'metrics': metrics,
        'sample_enriched_events': sampled,
        'reconstruction_summary': {
            'event_count': recon.get('event_sequence') and len(recon.get('event_sequence')) or 0,
            'quality': recon.get('event_reconstruction_quality')
        }
    }

# Save artifact
out_path = Path('rc4_sprint11b_event_reconstructor_reports.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(OUTPUT, f, ensure_ascii=False, indent=2)

print(f"Reports written to: {out_path}")
