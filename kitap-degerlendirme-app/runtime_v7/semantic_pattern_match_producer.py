from __future__ import annotations

import re
from typing import Any, Dict, List, Set

from runtime_v7.semantic_pattern_registry import get_sprint3_pattern_definitions

TITLE_FIELD_KEYWORDS = {
    'title',
    'book_title',
    'kitap_adi',
    'baslik',
    'başlık',
    'name',
}


def _fold_ascii(text: str) -> str:
    translation = str.maketrans({
        'ç': 'c', 'Ç': 'C', 'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I', 'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S', 'ü': 'u', 'Ü': 'U',
    })
    return text.translate(translation)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ''
    text = str(value)
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = _fold_ascii(text)
    return text.lower()


def _keyword_in_text(keyword: str, text: str) -> bool:
    keyword_norm = _normalize_text(keyword)
    if not keyword_norm:
        return False
    text_norm = _normalize_text(text)
    pattern = r'\b' + re.escape(keyword_norm) + r'\b'
    return re.search(pattern, text_norm) is not None


def _collect_strings(value: Any, parent_key: str = '') -> List[str]:
    texts: List[str] = []
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned:
            return [cleaned]
        return []

    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key or '').strip().lower()
            if any(token in normalized_key for token in TITLE_FIELD_KEYWORDS):
                continue
            texts.extend(_collect_strings(child, normalized_key))
        return texts

    if isinstance(value, list):
        for item in value:
            texts.extend(_collect_strings(item, parent_key))
        return texts

    return []


def _extract_summary_ir_texts(payload: dict) -> List[Dict[str, str]]:
    summary_ir = payload.get('summary_ir') or payload.get('canonical_summary_ir') or {}
    if not isinstance(summary_ir, dict):
        return []

    sources: List[Dict[str, str]] = []
    for key in ('themes', 'learning_outcomes', 'timeline'):
        items = summary_ir.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str) and item.strip():
                    sources.append({'source': f'summary_ir.{key}', 'text': item.strip()})
                elif isinstance(item, dict):
                    texts = _collect_strings(item, key)
                    for text in texts:
                        sources.append({'source': f'summary_ir.{key}', 'text': text})

    story_arc = summary_ir.get('story_arc')
    if isinstance(story_arc, str) and story_arc.strip():
        sources.append({'source': 'summary_ir.story_arc', 'text': story_arc.strip()})
    elif isinstance(story_arc, dict):
        for text in _collect_strings(story_arc, 'story_arc'):
            sources.append({'source': 'summary_ir.story_arc', 'text': text})

    narrative_graph = summary_ir.get('narrative_graph')
    if isinstance(narrative_graph, dict):
        for node in narrative_graph.get('nodes') or []:
            if isinstance(node, dict):
                node_text = node.get('summary') or node.get('action') or node.get('evidence') or ''
                if isinstance(node_text, str) and node_text.strip():
                    sources.append({'source': 'summary_ir.narrative_graph', 'text': node_text.strip()})

    return sources


def _extract_semantic_texts(payload: dict) -> List[Dict[str, str]]:
    semantic = payload.get('semantic') or {}
    if not isinstance(semantic, dict):
        semantic = {}

    sources: List[Dict[str, str]] = []
    for key in ('theme_clusters', 'character_roles', 'learning_outcome_clusters'):
        items = semantic.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str) and item.strip():
                    sources.append({'source': f'semantic.{key}', 'text': item.strip()})
                elif isinstance(item, dict):
                    for field in ('label', 'name', 'theme', 'role', 'outcome'):
                        field_value = item.get(field)
                        if isinstance(field_value, str) and field_value.strip():
                            sources.append({'source': f'semantic.{key}.{field}', 'text': field_value.strip()})
                    for text in _collect_strings(item, key):
                        sources.append({'source': f'semantic.{key}', 'text': text})

    return sources


def _extract_narrative_texts(payload: dict) -> List[Dict[str, str]]:
    narrative = payload.get('narrative') or {}
    if not isinstance(narrative, dict):
        return []

    sources: List[Dict[str, str]] = []
    for field in ('summary', 'text', 'story', 'overview', 'narrative_text'):
        value = narrative.get(field)
        if isinstance(value, str) and value.strip():
            sources.append({'source': f'narrative.{field}', 'text': value.strip()})

    for text in _collect_strings(narrative, 'narrative'):
        sources.append({'source': 'narrative.fields', 'text': text})

    return sources


def _find_matching_keywords(pattern_keywords: List[str], text: str) -> List[str]:
    matches: Set[str] = set()
    for keyword in pattern_keywords:
        if _keyword_in_text(keyword, text):
            matches.add(keyword)
    return sorted(matches)


def build_pattern_matches_from_payload(payload: dict) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    text_sources = (
        _extract_summary_ir_texts(payload)
        + _extract_semantic_texts(payload)
        + _extract_narrative_texts(payload)
    )
    if not text_sources:
        return []

    patterns = sorted(get_sprint3_pattern_definitions(), key=lambda p: str(p.get('id') or ''))
    matches: List[Dict[str, Any]] = []
    seen_keys: Set[str] = set()

    for pattern in patterns:
        pattern_id = str(pattern.get('id') or '').strip()
        if not pattern_id:
            continue
        category = str(pattern.get('category') or '').strip()
        name = str(pattern.get('name') or '').strip()
        keywords = [str(k) for k in pattern.get('keywords') or [] if str(k).strip()]
        if not keywords:
            continue

        for source_entry in text_sources:
            source = str(source_entry.get('source') or '').strip() or 'unknown'
            text = str(source_entry.get('text') or '').strip()
            if not text:
                continue
            matched_keywords = _find_matching_keywords(keywords, text)
            if not matched_keywords:
                continue

            key = f'{pattern_id}|{source}|{"|".join(matched_keywords)}|{text[:64]}'
            if key in seen_keys:
                continue
            seen_keys.add(key)

            matches.append({
                'pattern_id': pattern_id,
                'pattern_category': category,
                'pattern_name': name,
                'source': source,
                'matched_keywords': matched_keywords,
                'match_snippet': text if len(text) <= 256 else text[:253] + '...',
            })

    return sorted(matches, key=lambda x: (x['pattern_id'], x['source'], x['match_snippet']))
