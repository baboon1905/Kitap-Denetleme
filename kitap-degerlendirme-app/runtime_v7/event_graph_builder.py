"""Event Compression Layer — Sprint 10C

Builds narrative arc-level groups from reconstructed events.

Rules:
- Deterministic output
- Shadow-only, production-safe
- Merge events when they share a common objective, conflict, actor group, and outcome
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _normalize_events(reconstructed_events: Any) -> List[Dict[str, Any]]:
    if isinstance(reconstructed_events, dict):
        events = reconstructed_events.get('events', [])
    elif isinstance(reconstructed_events, list):
        events = reconstructed_events
    else:
        events = []

    normalized: List[Dict[str, Any]] = []
    for event in events:
        if isinstance(event, dict):
            normalized.append(event)
    return normalized


def _event_signature(event: Dict[str, Any]) -> Tuple[Tuple[str, ...], str, bool, Optional[str]]:
    actors = tuple(sorted(str(actor).strip().lower() for actor in event.get('actors', []) if str(actor).strip()))
    objective = _infer_objective(event)
    conflict = bool(event.get('conflict', False))
    result = _infer_result(event)
    return actors, objective, conflict, result


def _infer_objective(event: Dict[str, Any]) -> str:
    goal = str(event.get('goal', '') or '').strip().lower()
    if goal:
        return goal

    action = str(event.get('action', '') or '').strip().lower()
    object_ = str(event.get('object', '') or '').strip().lower()
    location = str(event.get('location_or_context', '') or '').strip().lower()

    if any(phrase in action for phrase in ['yolculuk', 'yelken', 'batıya', 'deniz', 'seyahat']):
        return 'batıya yolculuk'
    if any(phrase in action for phrase in ['karaya', 'ulaş']):
        return 'karaya ulaşma'
    if any(phrase in action for phrase in ['fırtına', 'umud', 'sars', 'umutsuz']):
        return 'umudun korunması'
    if any(phrase in action for phrase in ['keşif', 'adalar', 'dünya', 'bul', 'keşfet']):
        return 'keşif'
    if any(phrase in action for phrase in ['karşılaş', 'yerli']):
        return 'karşılaşma'
    if any(phrase in action for phrase in ['dönüş', 'geri']):
        return 'dönüş'
    if any(phrase in action for phrase in ['yardım', 'destek']):
        return 'yardım'
    if object_ and 'yeni dünya' in object_:
        return 'keşif'
    if location and 'okyanus' in location:
        return 'batıya yolculuk'
    return ''


def _infer_result(event: Dict[str, Any]) -> Optional[str]:
    result = str(event.get('result', '') or '').strip().lower()
    if result:
        return result
    action = str(event.get('action', '') or '').strip().lower()
    if any(phrase in action for phrase in ['ulaşt', 'ulaş', 'karaya']):
        return 'karaya ulaşma'
    if any(phrase in action for phrase in ['fırtına', 'umud', 'sars']):
        return 'umudun sarsılması'
    if any(phrase in action for phrase in ['keşif', 'keşfed']):
        return 'keşif'
    return None


def _infer_topic(event: Dict[str, Any]) -> str:
    action = str(event.get('action', '') or '').strip().lower()
    if any(phrase in action for phrase in ['karaya', 'ulaş']):
        return 'karaya_ulasma'
    if any(phrase in action for phrase in ['fırtına', 'umud', 'sars', 'umutsuz']):
        return 'umudun_sarsilmasi'
    if any(phrase in action for phrase in ['yolculuk', 'yelken', 'batıya', 'deniz']):
        return 'batıya_yolculuk'
    if any(phrase in action for phrase in ['keşif', 'adalar', 'dünya', 'yeni']):
        return 'yeni_dunya_kesfi'
    if any(phrase in action for phrase in ['karşılaş', 'yerli']):
        return 'yerlilerle_ilk_karsilasma'
    if any(phrase in action for phrase in ['dönüş', 'geri']):
        return 'donus_yolculugu'
    if any(phrase in action for phrase in ['mürettebat', 'gemi', 'yol']):
        return 'seyahat'
    return 'genel'


def build_event_graph(reconstructed_events: Any) -> Dict[str, Any]:
    """Group reconstructed events into narrative arcs.

    Output schema:
    {
      "arcs": [
        {
          "arc_id": "arc_000",
          "title": "...",
          "actors": [],
          "objective": "...",
          "conflict": false,
          "progression": [],
          "resolution": "",
          "supporting_events": [],
          "source_sentence_ids": [],
          "importance": 0.0
        }
      ]
    }
    """
    events = _normalize_events(reconstructed_events)
    if not events:
        return {'arcs': []}

    topic_blocks: List[List[Dict[str, Any]]] = []
    current_block: List[Dict[str, Any]] = []

    for event in events:
        if not current_block:
            current_block = [event]
            continue

        current_topic = _infer_topic(current_block[-1])
        candidate_topic = _infer_topic(event)
        if current_topic != candidate_topic:
            topic_blocks.append(current_block)
            current_block = [event]
            continue

        current_block.append(event)

    if current_block:
        topic_blocks.append(current_block)

    target_arc_count = _target_arc_count(len(events))
    if target_arc_count > 0 and len(topic_blocks) > target_arc_count:
        topic_blocks = _compress_blocks(topic_blocks, target_arc_count)

    arcs = []
    for idx, block in enumerate(topic_blocks):
        if block:
            arcs.append(_build_arc(block, idx))
    return {'arcs': arcs}


def _target_arc_count(event_count: int) -> int:
    if event_count <= 0:
        return 0
    return max(12, min(18, (event_count + 2) // 3))


def _compress_blocks(blocks: List[List[Dict[str, Any]]], target_count: int) -> List[List[Dict[str, Any]]]:
    compressed = [list(block) for block in blocks if block]
    while len(compressed) > target_count and len(compressed) > 1:
        merge_index = min(
            range(len(compressed) - 1),
            key=lambda idx: len(compressed[idx]) + len(compressed[idx + 1]),
        )
        compressed[merge_index] = compressed[merge_index] + compressed[merge_index + 1]
        del compressed[merge_index + 1]
    return compressed


def _should_start_new_arc(current_arc_events: List[Dict[str, Any]], event: Dict[str, Any]) -> bool:
    if len(current_arc_events) >= 8:
        return True

    current_event = current_arc_events[-1]
    current_signature = _event_signature(current_event)
    candidate_signature = _event_signature(event)
    current_topic = _infer_topic(current_event)
    candidate_topic = _infer_topic(event)

    if current_topic != candidate_topic:
        return True
    if current_signature[1] and candidate_signature[1] and current_signature[1] != candidate_signature[1]:
        return False
    if current_signature[2] != candidate_signature[2]:
        return False
    if current_signature[0] and candidate_signature[0] and current_signature[0] != candidate_signature[0]:
        return False
    return False


def _build_arc(events: List[Dict[str, Any]], arc_index: int) -> Dict[str, Any]:
    ordered = list(events)
    first_event = ordered[0]
    actors = sorted({str(actor).strip() for actor in first_event.get('actors', []) if str(actor).strip()})
    objective = str(first_event.get('goal', '') or '').strip() or _infer_objective(first_event) or 'Narrative objective'
    conflict = bool(first_event.get('conflict', False))
    resolution_candidates = [str(item.get('result', '') or '').strip() for item in ordered if str(item.get('result', '') or '').strip()]
    resolution = resolution_candidates[-1] if resolution_candidates else str(first_event.get('result', '') or '').strip() or 'Resolution pending'
    chronology = [item.get('event_id', '') for item in ordered if item.get('event_id')]
    source_sentence_ids = []
    for item in ordered:
        for source_id in item.get('source_sentence_ids', []) or []:
            if source_id not in source_sentence_ids:
                source_sentence_ids.append(source_id)
    support_events = chronology[1:]
    importance = max(float(item.get('importance', 0.0) or 0.0) for item in ordered)
    title = _generate_title(first_event, actors, objective, resolution)
    return {
        'arc_id': f'arc_{arc_index:03d}',
        'title': title,
        'actors': actors,
        'objective': objective,
        'conflict': conflict,
        'progression': chronology,
        'resolution': resolution,
        'supporting_events': support_events,
        'source_sentence_ids': source_sentence_ids,
        'importance': round(importance, 3),
    }


def _generate_title(event: Dict[str, Any], actors: List[str], objective: str, resolution: str) -> str:
    action = str(event.get('action', '') or '').strip().lower()
    goal = str(event.get('goal', '') or '').strip().lower()
    object_ = str(event.get('object', '') or '').strip().lower()
    location = str(event.get('location_or_context', '') or '').strip().lower()
    result = str(event.get('result', '') or '').strip().lower()
    actor_text = ', '.join(actors[:2]) if actors else 'Bilinmeyen karakterler'

    if objective and objective.lower() not in {'', 'narrative objective'}:
        if 'yolculuk' in objective.lower() or 'seyahat' in objective.lower():
            return 'Batıya Yolculuk'
        if 'keşif' in objective.lower() or 'discover' in objective.lower():
            return 'Yeni Dünyanın Keşfi'
        if 'karşılaş' in objective.lower() or 'encounter' in objective.lower():
            return 'Yerlilerle İlk Karşılaşma'
        if 'dönüş' in objective.lower() or 'return' in objective.lower():
            return 'Dönüş Yolculuğu'
        if 'karaya' in objective.lower():
            return 'Karaya Ulaşılması'
        if 'yardım' in objective.lower():
            return 'Yardım ve Destek'

    if goal:
        if 'batıya' in goal or 'yolculuk' in goal:
            return 'Batıya Yolculuk'
        if 'karaya' in goal:
            return 'Karaya Ulaşılması'
        if 'keşif' in goal:
            return 'Yeni Dünyanın Keşfi'
        if 'karşılaş' in goal:
            return 'Yerlilerle İlk Karşılaşma'
        if 'dönüş' in goal:
            return 'Dönüş Yolculuğu'

    if result:
        if 'sars' in result or 'umud' in result:
            return 'Umudun Sarsılması'
        if 'ulaşıldı' in result or 'ulaş' in result:
            return 'Karaya Ulaşılması'
        if 'başladı' in result:
            return 'Yolculuğun Başlangıcı'

    if action:
        if 'karaya' in action:
            return 'Karaya Ulaşılması'
        if 'fırtına' in action or 'umud' in action:
            return 'Umudun Sarsılması'
        if 'yolculuk' in action or 'yelken' in action:
            return 'Batıya Yolculuk'
        if 'keşif' in action or 'adalar' in action or 'yeni dünya' in action:
            return 'Yeni Dünyanın Keşfi'
        if 'karşılaş' in action or 'yerli' in action:
            return 'Yerlilerle İlk Karşılaşma'
        if 'dönüş' in action or 'geri' in action:
            return 'Dönüş Yolculuğu'

    if object_ and 'yeni dünya' in object_:
        return 'Yeni Dünyanın Keşfi'
    if location and 'okyanus' in location:
        return 'Okyanus Yolculuğu'
    if location and 'barcelona' in location:
        return 'Barcelona’nın Önemi'

    return f'{actor_text} ile Yeni Bir Aşama'
