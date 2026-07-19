"""Shadow-only semantic event merger for RC4 Sprint 12E.1.

This module merges similar and adjacent evidence events into a single semantic
event without touching the production pipeline. It accepts filtered evidence
items or reconstructed-event-like dictionaries and returns structured merge
metrics.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def _coerce_text(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        for key in ("text", "action", "content", "sentence", "summary"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""
    return str(item).strip()


def _coerce_source_ids(item: Any) -> List[str]:
    if isinstance(item, dict):
        raw = item.get("source_sentence_ids") or item.get("source_sentence_id") or item.get("sentence_id") or item.get("source_id")
        if isinstance(raw, list):
            return [str(v).strip() for v in raw if str(v).strip()]
        if isinstance(raw, str) and raw.strip():
            return [raw.strip()]
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            return [str(int(raw))]
    return []


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [token for token in re.findall(r"[a-zçğıöşü]+", text.lower()) if len(token) > 1]


def _jaccard_similarity(a: Sequence[str], b: Sequence[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    sa = set(a)
    sb = set(b)
    return len(sa & sb) / len(sa | sb)


def _token_overlap(a: Sequence[str], b: Sequence[str]) -> float:
    if not a or not b:
        return 0.0
    sa = set(a)
    sb = set(b)
    return len(sa & sb) / min(len(sa), len(sb))


def _normalize_section(item: Any) -> str:
    if isinstance(item, dict):
        section = item.get("section") or item.get("narrative_section") or item.get("type")
        if isinstance(section, str) and section.strip():
            return section.strip().lower()
    return "events"


def _normalize_narrative_role(item: Any) -> str:
    if isinstance(item, dict):
        role = item.get("narrative_role") or item.get("role") or item.get("narrative_function")
        if isinstance(role, str) and role.strip():
            return role.strip().lower()
    return ""


def _should_merge(left: Dict[str, Any], right: Dict[str, Any]) -> bool:
    left_text = left["text"]
    right_text = right["text"]
    left_tokens = _tokenize(left_text)
    right_tokens = _tokenize(right_text)

    if not left_text or not right_text:
        return False

    if left["section"] != right["section"]:
        return False

    if left["section"] in {"conflict", "resolution"}:
        return False

    jaccard = _jaccard_similarity(left_tokens, right_tokens)
    overlap = _token_overlap(left_tokens, right_tokens)
    shared_content_tokens = len(set(left_tokens) & set(right_tokens))
    same_role = left["narrative_role"] and right["narrative_role"] and left["narrative_role"] == right["narrative_role"]

    if shared_content_tokens >= 2 and (same_role or left["section"] in {"events", "setup"} and right["section"] in {"events", "setup"}) and (jaccard >= 0.05 or overlap >= 0.2):
        return True
    if shared_content_tokens >= 1 and (same_role or left["section"] in {"events", "setup"} and right["section"] in {"events", "setup"}) and (jaccard >= 0.03 or overlap >= 0.15):
        return True
    if len(left_tokens) <= 4 and len(right_tokens) <= 4 and (shared_content_tokens >= 1 or overlap >= 0.1):
        return True
    if overlap >= 0.2 and len(left_tokens) <= 6 and len(right_tokens) <= 6:
        return True
    return False


def merge_semantic_events(events: Any) -> Dict[str, Any]:
    """Merge similar and adjacent events into semantic events.

    The input may be either a list of evidence/reconstructed-event-like items or
    a sectioned dict such as {'setup': [...], 'events': [...]}.

    Output contract:
    {
        'merged_events': [...],
        'input_event_count': int,
        'output_event_count': int,
        'merge_ratio': float,
        'source_sentence_id_preservation_rate': float,
        'deterministic': bool,
        'production_output_changed': bool,
        'runtime_pipeline_bound': bool,
    }
    """

    if isinstance(events, dict):
        ordered_items: List[Any] = []
        for section in ("setup", "conflict", "events", "resolution"):
            items = events.get(section, [])
            if isinstance(items, list):
                for item in items:
                    ordered_items.append(item)
    elif isinstance(events, list):
        ordered_items = events
    else:
        ordered_items = []

    normalized_items: List[Dict[str, Any]] = []
    for item in ordered_items:
        text = _coerce_text(item)
        if not text:
            continue
        normalized_item = {
            "text": text,
            "source_sentence_ids": _coerce_source_ids(item),
            "section": _normalize_section(item),
            "narrative_role": _normalize_narrative_role(item),
            "supporting_evidence_ids": _coerce_source_ids(item),
            "evidence_count": 1,
        }
        if isinstance(item, dict):
            for key, value in item.items():
                if key not in {"text", "source_sentence_ids", "supporting_evidence_ids", "evidence_count"}:
                    normalized_item[key] = value
        normalized_items.append(normalized_item)

    merged: List[Dict[str, Any]] = []
    for item in normalized_items:
        if not merged:
            merged.append(dict(item))
            continue

        last = merged[-1]
        if _should_merge(last, item):
            last["text"] = f"{last['text']} {item['text']}"
            last["source_sentence_ids"] = list(OrderedDict.fromkeys(last.get("source_sentence_ids", []) + item.get("source_sentence_ids", [])))
            last["supporting_evidence_ids"] = list(OrderedDict.fromkeys(last.get("supporting_evidence_ids", []) + item.get("supporting_evidence_ids", [])))
            last["evidence_count"] = last.get("evidence_count", 1) + 1
        else:
            merged.append(dict(item))

    if not merged:
        return {
            "merged_events": [],
            "input_event_count": 0,
            "output_event_count": 0,
            "merge_ratio": 0.0,
            "source_sentence_id_preservation_rate": 1.0,
            "deterministic": True,
            "production_output_changed": False,
            "runtime_pipeline_bound": False,
        }

    output_count = len(merged)
    merge_ratio = output_count / len(normalized_items) if normalized_items else 0.0

    input_count = len(normalized_items)
    output_count = len(merged)
    merge_ratio = output_count / input_count if input_count else 0.0

    total_source_ids = sum(len(item.get("source_sentence_ids", [])) for item in normalized_items)
    preserved_source_ids = sum(len(item.get("source_sentence_ids", [])) for item in merged)
    preservation_rate = preserved_source_ids / total_source_ids if total_source_ids else 1.0

    return {
        "merged_events": merged,
        "input_event_count": input_count,
        "output_event_count": output_count,
        "merge_ratio": round(merge_ratio, 3),
        "source_sentence_id_preservation_rate": round(preservation_rate, 3),
        "deterministic": True,
        "production_output_changed": False,
        "runtime_pipeline_bound": False,
    }
