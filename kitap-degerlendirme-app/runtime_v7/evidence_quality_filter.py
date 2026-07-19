import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

NOISE_PATTERNS = [
    r"^sayfa\b",
    r"^sayf\b",
    r"^page\b",
    r"^pdf\b",
    r"^docx?\b",
    r"^word\b",
    r"^dosya\b",
    r"^meta\b",
    r"^source\b",
    r"^http[s]?://",
    r"^www\.",
    r"^\d+$",
]
COMMON_STOPWORDS = {
    've', 'ile', 'bir', 'bu', 'o', 'da', 'de', 'mi', 'ne', 'ki', 'su', 'gibi', 'ama', 'fakat', 'veya', 'ya', 'ya da'
}
QUALITY_MARKERS = {
    'dür', 'dır', 'mış', 'miş', 'sonuç', 'zorluk', 'karşı', 'öğrendi', 'başarı', 'görev', 'kaçamak', 'gidecek', 'amcasına', 'çiftliğe',
    'karar', 'çatışma', 'değişim', 'sonuç', 'çözüm', 'kayıp', 'bulma', 'gitme', 'kaçma', 'dönme', 'yardım', 'isteme'
}
RETENTION_RANGES = {
    'setup': (0.55, 0.80),
    'conflict': (0.70, 0.95),
    'events': (0.50, 0.75),
    'resolution': (0.70, 0.95),
}
OCR_FRAGMENT_SUFFIXES = {
    'le', 'la', 'li', 'lı', 'lu', 'lü', 'ca', 'ce', 'ci', 'cı', 'cu', 'cü',
    'ma', 'me', 'mış', 'miş', 'muş', 'müş', 'mı', 'mi', 'mu', 'mü',
    'dı', 'di', 'du', 'dü', 'dir', 'dır', 'dur', 'dür', 'li', 'lı', 'lu', 'lü',
    'nı', 'ni', 'nu', 'nü', 'm', 'n', 'k', 'ğım', 'ğim', 'ğüm', 'güm', 'dan', 'den', 'den', 'dan',
}


def normalize_text(text: Any) -> str:
    """Normalize extracted evidence text for filtering and contract output."""
    if text is None:
        return ''
    text_str = str(text)
    text_str = text_str.replace('\u00a0', ' ')
    text_str = re.sub(r'[\r\n\t]+', ' ', text_str)
    text_str = re.sub(r'\s+', ' ', text_str).strip()
    text_str = re.sub(r'(?i)\b(sayfa|page|pdf|docx|word|dosya|meta)\s*[:\-]?\s*\d+\b', '', text_str)
    text_str = re.sub(r'\b(PDF|pdf|DOCX|docx|Word|word)\b', '', text_str)
    text_str = re.sub(r'\s*[-=]{2,}\s*', ' ', text_str)
    text_str = re.sub(r'\s+([\.,:;\?!])', r'\1', text_str)
    text_str = re.sub(r'([\.,:;\?!])(?=[^\s])', r'\1 ', text_str)
    text_str = text_str.replace('\xad', '')

    # Strip page digit artifacts stuck to words.
    text_str = re.sub(r'\b\d+(?=[A-Za-zÇĞİÖŞÜçğıöşü])', '', text_str)
    text_str = re.sub(r'(?<=[A-Za-zÇĞİÖŞÜçğıöşü])\d+\b', '', text_str)

    # Repair common PDF split-word fragments and OCR spacing artifacts.
    repairs = {
        r'\bam ca sı na\b': 'amcasına',
        r'\bka ça mak\b': 'kaçamak',
        r'\bgi de cek\b': 'gidecek',
        r'\bÇift li ğe\b': 'Çiftliğe',
        r'\bçift li ğe\b': 'çiftliğe',
    }
    for pattern, replacement in repairs.items():
        text_str = re.sub(pattern, replacement, text_str, flags=re.IGNORECASE)

    # Repair common PDF split-word fragments with short suffix tokens.
    text_str = re.sub(
        r'\b([A-Za-zÇĞİÖŞÜçğıöşü]{3,})\s+(li|lı|lu|lü|ci|cı|cu|cü|de|da|ta|te|dir|dır|dur|dür|si|sı|su|sü)\s+(ğe|ge|ya|ye|yi|yu|yü)\b',
        lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}",
        text_str,
        flags=re.IGNORECASE,
    )
    text_str = re.sub(
        r'\b([A-Za-zÇĞİÖŞÜçğıöşü]{3,})\s+(li|lı|lu|lü|ci|cı|cu|cü|de|da|ta|te|dir|dır|dur|dür|si|sı|su|sü)\b',
        lambda m: f"{m.group(1)}{m.group(2)}",
        text_str,
        flags=re.IGNORECASE,
    )

    text_str = re.sub(r'\s+', ' ', text_str).strip()
    return text_str


def is_noise(text: str) -> bool:
    """Decide whether a normalized sentence is noise rather than evidence."""
    if not text:
        return True
    normalized = text.strip().lower()
    if len(normalized) < 20:
        if any(re.match(pattern, normalized) for pattern in NOISE_PATTERNS):
            return True
        if len(re.findall(r'[a-zçğıöşü]', normalized)) < 5:
            return True
        if normalized in {'...', '..', '-', '—', '–'}:
            return True
    if normalized.startswith('sayfa ') or normalized.startswith('page '):
        return True
    if normalized.startswith('dosya ') or normalized.startswith('pdf '):
        return True
    if normalized.endswith('sayfa') and len(normalized.split()) <= 3:
        return True
    return False


def _extract_source_ids(item: Any) -> List[str]:
    ids = []
    if isinstance(item, dict):
        for key in ('source_sentence_ids', 'source_sentence_id', 'sentence_id', 'source_id', 'source'):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                ids.append(value.strip())
            elif isinstance(value, list):
                ids.extend([str(v).strip() for v in value if isinstance(v, str) and v.strip()])
    return ids


def _normalize_for_dedupe(text: str) -> str:
    return re.sub(r'[^a-z0-9çğıöşü]', '', text.lower())


def _token_set(text: str) -> set:
    return {
        token for token in re.findall(r'[a-zçğıöşü]+', text.lower())
        if token not in COMMON_STOPWORDS
    }


def _jaccard_similarity(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _token_overlap(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _has_fragmented_ocr(text: str) -> bool:
    normalized = text.lower()
    if re.search(r'\b(?:[a-zçğıöşü]{1,3}\s+){3,}[a-zçğıöşü]{1,3}\b', normalized):
        return True
    if re.search(r'\b\d+[a-zçğıöşü]|[a-zçğıöşü]\d+\b', normalized):
        return True
    tokens = normalized.split()
    short_tokens = [t for t in tokens if len(t) <= 2 and t not in COMMON_STOPWORDS and t.isalpha()]
    if len(short_tokens) >= 3:
        return True
    return False


def _normalize_ocr_fragment_tokens(text: str) -> str:
    normalized = text
    normalized = re.sub(r'\b(göz)\s+le\s+ri\b', r'\1leri', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(yaş)\s+la\s+ra\b', r'\1lara', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(yaş)\s+la\s+ri\b', r'\1lari', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(göz)\s+le\s+ri\b', r'\1leri', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(dol)\s+muş\s+tu\b', r'\1muştu', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(am)\s+ca\s+cı\s+ğım\b', r'amcacığım', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(am)\s+ca\s+cı\s+ğım\b', r'amcacığım', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(ka)\s+ça\s+mak\b', r'kaçamak', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(gi)\s+de\s+cek\b', r'gidecek', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(ge)\s+le\s+cek\b', r'gelecek', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(Çift)\s+li\s+ğe\b', r'Çiftliğe', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\b(çift)\s+li\s+ğe\b', r'çiftliğe', normalized, flags=re.IGNORECASE)
    # Join common fragment patterns like "kel im" -> "kelim" when token boundaries are likely OCR splits.
    normalized = re.sub(r'\b([a-zçğıöşü]{2,})\s+([a-zçğıöşü]{2,})\b', lambda m: m.group(1) + m.group(2) if m.group(2) in OCR_FRAGMENT_SUFFIXES else m.group(0), normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def _normalize_evidence_item(item: Any) -> Dict[str, Any]:
    if isinstance(item, str):
        raw_text = item
    elif isinstance(item, dict):
        raw_text = item.get('text') or item.get('metin') or item.get('alinti') or item.get('evidence') or ''
    else:
        raw_text = str(item)

    normalized = normalize_text(raw_text)
    original_normalized = normalized
    repaired_text = _normalize_ocr_fragment_tokens(normalized)
    if isinstance(item, dict):
        source_ids = _extract_source_ids(item)
    else:
        source_ids = []

    return {
        'text': repaired_text,
        'original_normalized_text': original_normalized,
        'source_sentence_ids': source_ids,
        'raw_text': raw_text,
        'raw': item,
    }


def deduplicate_evidence(evidence_items: Iterable[Any]) -> Tuple[List[Dict[str, Any]], int]:
    """Remove exact and semantic duplicate evidence items while preserving source IDs and order."""
    output: List[Dict[str, Any]] = []
    seen: List[Dict[str, Any]] = []
    removed = 0
    for item in evidence_items:
        if isinstance(item, dict) and 'text' in item and 'source_sentence_ids' in item:
            normalized_item = dict(item)
            normalized_item['text'] = normalize_text(normalized_item['text'])
            normalized_item['source_sentence_ids'] = normalized_item.get('source_sentence_ids') or []
        else:
            normalized_item = _normalize_evidence_item(item)

        if not normalized_item['text']:
            removed += 1
            continue

        key = _normalize_for_dedupe(normalized_item['text'])
        if key:
            exact_match = next((existing for existing in seen if _normalize_for_dedupe(existing['text']) == key), None)
            if exact_match is not None:
                combined_ids = list(dict.fromkeys(exact_match.get('source_sentence_ids', []) + normalized_item.get('source_sentence_ids', [])))
                exact_match['source_sentence_ids'] = combined_ids
                removed += 1
                continue

        candidate_tokens = _token_set(normalized_item['text'])
        semantic_match = None
        for existing in seen:
            existing_tokens = _token_set(existing['text'])
            jaccard = _jaccard_similarity(candidate_tokens, existing_tokens)
            overlap = _token_overlap(candidate_tokens, existing_tokens)
            size_ratio = min(len(candidate_tokens), len(existing_tokens)) / max(len(candidate_tokens), len(existing_tokens)) if candidate_tokens and existing_tokens else 0.0
            if (jaccard >= 0.45 and overlap >= 0.66 and size_ratio >= 0.66):
                semantic_match = existing
                break

        if semantic_match is not None:
            combined_ids = list(dict.fromkeys(semantic_match.get('source_sentence_ids', []) + normalized_item.get('source_sentence_ids', [])))
            semantic_match['source_sentence_ids'] = combined_ids
            removed += 1
            continue

        seen.append(normalized_item)
        output.append(normalized_item)
    return output, removed


def deduplicate_exact_evidence(evidence_items: Iterable[Any]) -> Tuple[List[Dict[str, Any]], int]:
    """Remove exact duplicate evidence items while preserving source IDs and order."""
    output: List[Dict[str, Any]] = []
    seen: Dict[str, Dict[str, Any]] = {}
    removed = 0
    for item in evidence_items:
        normalized_item = dict(item) if isinstance(item, dict) else _normalize_evidence_item(item)
        normalized_item['text'] = normalize_text(normalized_item['text'])
        normalized_item['source_sentence_ids'] = normalized_item.get('source_sentence_ids') or []
        if not normalized_item['text']:
            removed += 1
            continue

        key = _normalize_for_dedupe(normalized_item['text'])
        if key in seen:
            existing = seen[key]
            combined_ids = list(dict.fromkeys(existing.get('source_sentence_ids', []) + normalized_item.get('source_sentence_ids', [])))
            existing['source_sentence_ids'] = combined_ids
            removed += 1
            continue

        seen[key] = normalized_item
        output.append(normalized_item)
    return output, removed


def _semantic_score(text: str, section: str) -> float:
    score = 0.4
    if len(text) > 80:
        score += 0.25
    if section == 'conflict':
        score += 0.15
    if section == 'resolution':
        score += 0.15
    if any(marker in text.lower() for marker in QUALITY_MARKERS):
        score += 0.1
    tokens = re.findall(r'[a-zçğıöşü]+', text.lower())
    short_tokens = [t for t in tokens if len(t) <= 2 and t not in COMMON_STOPWORDS]
    if len(short_tokens) >= 3:
        score -= 0.15
    if re.search(r'\d', text):
        score -= 0.1
    return max(0.0, min(1.0, score))


def _ocr_quality_score(text: str) -> float:
    score = 0.9
    if _has_fragmented_ocr(text):
        score -= 0.35
    if len(text) < 30:
        score -= 0.15
    if re.search(r'\d', text):
        score -= 0.05
    return max(0.0, min(1.0, score))


def _final_quality_score(text: str, section: str, ocr_text: Optional[str] = None) -> float:
    semantic = _semantic_score(text, section)
    ocr_input = ocr_text if ocr_text is not None else text
    ocr = _ocr_quality_score(ocr_input)
    final = semantic * 0.80 + ocr * 0.20
    if _has_fragmented_ocr(ocr_input):
        final = max(0.0, final - 0.15)
    return max(0.0, min(1.0, final))


def filter_summary_ir_evidence(summary_ir: Dict[str, Any]) -> Dict[str, Any]:
    """Filter summary_ir evidence snippets and return a deterministic contract."""
    if not isinstance(summary_ir, dict):
        raise ValueError('summary_ir must be a dict')

    sections = ['setup', 'conflict', 'events', 'resolution']
    input_count = 0
    noise_removed = 0
    low_quality_removed = 0
    removed_reasons: Dict[str, int] = {'noise': 0, 'low_quality': 0, 'duplicate': 0}
    duplicates_removed = 0
    section_input_counts: Dict[str, int] = {section: 0 for section in sections}
    filtered_evidence: Dict[str, List[Dict[str, Any]]] = {section: [] for section in sections}

    raw_candidates: Dict[str, List[Dict[str, Any]]] = {section: [] for section in sections}
    for section in sections:
        raw_items = summary_ir.get('evidence_snippets', {}).get(section, [])
        if not isinstance(raw_items, list):
            continue
        section_input_counts[section] = len(raw_items)
        for index, item in enumerate(raw_items):
            input_count += 1
            normalized_item = _normalize_evidence_item(item)
            normalized_item['original_index'] = index
            if is_noise(normalized_item['text']):
                noise_removed += 1
                removed_reasons['noise'] += 1
                continue
            raw_candidates[section].append(normalized_item)

    semantic_scores_before: List[float] = []
    ocr_scores_before: List[float] = []
    final_scores_before: List[float] = []
    mandatory_preserved_count = 0
    candidate_buckets: Dict[str, List[Dict[str, Any]]] = {section: [] for section in sections}
    for section, items in raw_candidates.items():
        for item in items:
            semantic = _semantic_score(item['text'], section)
            ocr_input_text = item.get('original_normalized_text', item['text'])
            ocr = _ocr_quality_score(ocr_input_text)
            final = _final_quality_score(item['text'], section, ocr_input_text)
            fragmented = _has_fragmented_ocr(ocr_input_text)
            marker = any(marker in item['text'].lower() for marker in QUALITY_MARKERS)
            item.update({
                'semantic_score': round(semantic, 3),
                'ocr_quality_score': round(ocr, 3),
                'final_quality_score': round(final, 3),
                'fragmented_ocr': fragmented,
                'quality_marker': marker,
                'low_quality': final <= 0.30 and not marker,
                'retained': False,
                'removal_reason': None,
            })
            semantic_scores_before.append(semantic)
            ocr_scores_before.append(ocr)
            final_scores_before.append(final)
            candidate_buckets[section].append(item)

    section_output_counts: Dict[str, int] = {}
    section_retention_rates: Dict[str, float] = {}
    section_available_counts: Dict[str, int] = {}
    section_retention_shortfall_counts: Dict[str, int] = {}
    section_retention_shortfall_reasons: Dict[str, str] = {}
    total_retention_shortfall_count = 0
    total_retention_shortfall_reasons = set()

    for section, items in candidate_buckets.items():
        if not items:
            section_output_counts[section] = 0
            section_retention_rates[section] = 0.0
            section_available_counts[section] = 0
            section_retention_shortfall_counts[section] = 0
            section_retention_shortfall_reasons[section] = ''
            continue

        for item in items:
            item['dedupe_key'] = _normalize_for_dedupe(item['text'])

        lo, hi = RETENTION_RANGES[section]
        preserve_count = max(int(math.ceil(section_input_counts.get(section, 0) * lo)), 1)
        max_preserve = max(int(math.floor(section_input_counts.get(section, 0) * hi)), preserve_count)

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            groups.setdefault(item['dedupe_key'], []).append(item)

        group_scores = []
        for dedupe_key, group_items in groups.items():
            representative = sorted(
                group_items,
                key=lambda item: (
                    item['final_quality_score'],
                    item['semantic_score'],
                    item['ocr_quality_score'],
                    len(item['source_sentence_ids']),
                    -item['original_index'],
                ),
                reverse=True,
            )[0]
            group_scores.append({
                'dedupe_key': dedupe_key,
                'representative': representative,
                'group_items': group_items,
                'group_size': len(group_items),
                'is_mandatory': representative['quality_marker'],
                'is_low_quality': representative['low_quality'],
            })

        section_available_counts[section] = len(group_scores)
        shortfall_count = max(preserve_count - len(group_scores), 0)
        section_retention_shortfall_counts[section] = shortfall_count
        if shortfall_count > 0:
            section_retention_shortfall_reasons[section] = 'insufficient_candidates_after_noise_and_dedupe'
            total_retention_shortfall_count += shortfall_count
            total_retention_shortfall_reasons.add(section_retention_shortfall_reasons[section])
        else:
            section_retention_shortfall_reasons[section] = ''

        group_scores.sort(
            key=lambda entry: (
                entry['representative']['final_quality_score'],
                entry['representative']['semantic_score'],
                entry['representative']['ocr_quality_score'],
                len(entry['representative']['source_sentence_ids']),
                -entry['representative']['original_index'],
            ),
            reverse=True,
        )

        mandatory_groups = [entry for entry in group_scores if entry['is_mandatory']]
        other_groups = [entry for entry in group_scores if not entry['is_mandatory']]

        selected_groups: List[Dict[str, Any]] = []
        selected_keys = set()

        for entry in mandatory_groups:
            selected_groups.append(entry)
            selected_keys.add(entry['dedupe_key'])
            if entry['is_low_quality']:
                mandatory_preserved_count += 1

        for entry in other_groups:
            if len(selected_groups) >= preserve_count:
                break
            selected_groups.append(entry)
            selected_keys.add(entry['dedupe_key'])

        if len(selected_groups) < preserve_count:
            for entry in other_groups:
                if entry['dedupe_key'] in selected_keys:
                    continue
                selected_groups.append(entry)
                selected_keys.add(entry['dedupe_key'])
                if len(selected_groups) >= preserve_count:
                    break

        if len(selected_groups) < preserve_count:
            # Not enough eligible groups to satisfy the preservation floor.
            # This is reported as a shortfall, but we still keep every available group.
            for entry in other_groups:
                if entry['dedupe_key'] in selected_keys:
                    continue
                selected_groups.append(entry)
                selected_keys.add(entry['dedupe_key'])

        if len(selected_groups) > max_preserve:
            mandatory_selected = [entry for entry in selected_groups if entry['is_mandatory']]
            non_mandatory_selected = [entry for entry in selected_groups if not entry['is_mandatory']]
            non_mandatory_cap = max(max_preserve - len(mandatory_selected), 0)
            selected_groups = mandatory_selected + non_mandatory_selected[:non_mandatory_cap]
            selected_keys = {entry['dedupe_key'] for entry in selected_groups}

        for entry in group_scores:
            if entry['dedupe_key'] not in selected_keys and entry['is_low_quality']:
                low_quality_removed += len(entry['group_items'])
                removed_reasons['low_quality'] += len(entry['group_items'])

        for entry in selected_groups:
            representative = entry['representative']
            combined_ids = []
            for item in entry['group_items']:
                ids = item.get('source_sentence_ids') or []
                for source_id in ids:
                    if source_id not in combined_ids:
                        combined_ids.append(source_id)
            representative['source_sentence_ids'] = combined_ids
            representative['retained'] = True
            representative['removal_reason'] = 'retained'
            filtered_evidence[section].append(representative)
            duplicates_removed += max(0, entry['group_size'] - 1)

        deduped, section_duplicates_removed = deduplicate_exact_evidence(filtered_evidence[section])
        duplicates_removed += section_duplicates_removed
        removed_reasons['duplicate'] += section_duplicates_removed
        filtered_evidence[section] = sorted(deduped, key=lambda item: item.get('original_index', 0))
        for item in filtered_evidence[section]:
            item['retained'] = True
            if item.get('removal_reason') is None:
                item['removal_reason'] = 'retained'

        section_output_counts[section] = len(filtered_evidence[section])
        section_retention_rates[section] = round(section_output_counts[section] / section_input_counts.get(section, 0), 3) if section_input_counts.get(section, 0) else 0.0

    semantic_scores_after = [item['semantic_score'] for items in filtered_evidence.values() for item in items]
    ocr_scores_after = [item['ocr_quality_score'] for items in filtered_evidence.values() for item in items]
    final_scores_after = [item['final_quality_score'] for items in filtered_evidence.values() for item in items]

    avg_semantic_score_before = round(sum(semantic_scores_before) / len(semantic_scores_before), 3) if semantic_scores_before else 0.0
    avg_ocr_quality_score_before = round(sum(ocr_scores_before) / len(ocr_scores_before), 3) if ocr_scores_before else 0.0
    avg_final_quality_score_before = round(sum(final_scores_before) / len(final_scores_before), 3) if final_scores_before else 0.0
    avg_semantic_score_after = round(sum(semantic_scores_after) / len(semantic_scores_after), 3) if semantic_scores_after else 0.0
    avg_ocr_quality_score_after = round(sum(ocr_scores_after) / len(ocr_scores_after), 3) if ocr_scores_after else 0.0
    avg_final_quality_score_after = round(sum(final_scores_after) / len(final_scores_after), 3) if final_scores_after else 0.0

    output_count = sum(len(items) for items in filtered_evidence.values())
    reduction_rate = round((input_count - output_count) / input_count, 3) if input_count else 0.0
    retention_shortfall_count = total_retention_shortfall_count
    retention_shortfall_reason = ';'.join(sorted(total_retention_shortfall_reasons)) if total_retention_shortfall_reasons else ''

    return {
        'filtered_evidence': filtered_evidence,
        'metrics': {
            'input_count': input_count,
            'output_count': output_count,
            'reduction_rate': reduction_rate,
            'noise_removed': noise_removed,
            'low_quality_removed': low_quality_removed,
            'mandatory_preserved_count': mandatory_preserved_count,
            'removed_reasons': removed_reasons,
            'duplicates_removed': duplicates_removed,
            'avg_semantic_score_before': avg_semantic_score_before,
            'avg_ocr_quality_score_before': avg_ocr_quality_score_before,
            'avg_final_quality_score_before': avg_final_quality_score_before,
            'avg_quality_score_before': avg_final_quality_score_before,
            'avg_semantic_score_after': avg_semantic_score_after,
            'avg_ocr_quality_score_after': avg_ocr_quality_score_after,
            'avg_final_quality_score_after': avg_final_quality_score_after,
            'avg_quality_score_after': avg_final_quality_score_after,
            'quality_retention_ranges': RETENTION_RANGES,
            'section_input_counts': section_input_counts,
            'section_output_counts': section_output_counts,
            'section_available_counts': section_available_counts,
            'section_retention_rates': section_retention_rates,
            'section_retention_shortfall_counts': section_retention_shortfall_counts,
            'section_retention_shortfall_reasons': section_retention_shortfall_reasons,
            'retention_shortfall_count': retention_shortfall_count,
            'retention_shortfall_reason': retention_shortfall_reason,
        },
    }
