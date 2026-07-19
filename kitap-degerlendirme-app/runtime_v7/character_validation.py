from __future__ import annotations

from typing import Any, Dict, List, Optional, Set


def _normalize_value_to_float(value: Any) -> float:
    if isinstance(value, (float, int)):
        value = float(value)
    elif isinstance(value, str):
        try:
            value = float(value.replace(",", "."))
        except Exception:
            value = 0.0
    else:
        value = 0.0

    if value is None:
        return 0.0
    try:
        value = float(value)
    except Exception:
        return 0.0

    if value > 1.0:
        value = value / 100.0
    return max(0.0, min(0.99, value))


def _normalize_character_name(item: Any) -> str:
    if isinstance(item, dict):
        return str(
            item.get("ad")
            or item.get("karakter_adi")
            or item.get("entity_name")
            or item.get("name")
            or ""
        ).strip()
    if isinstance(item, str):
        return item.strip()
    return ""


def _extract_character_items(payload: dict) -> List[Dict[str, Any]]:
    characters: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for item in payload.get("ana_karakterler") or []:
        if not isinstance(item, dict):
            continue
        name = _normalize_character_name(item)
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        mention_count = int(item.get("mention_count") or item.get("gorunum_sayisi") or item.get("frequency") or 0)
        relation_score = _normalize_value_to_float(item.get("relation_score") or item.get("centrality_score") or item.get("iliski_skoru") or 0.0)
        confidence = _normalize_value_to_float(item.get("guven_skoru") or item.get("confidence") or item.get("entity_confidence") or relation_score)
        characters.append(
            {
                "name": name,
                "mention_count": mention_count,
                "relation_score": relation_score,
                "confidence": confidence,
                "central": bool(item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi")),
            }
        )

    # Add actors from event graph if no explicit characters or if there are extra actor names.
    narrative_graph = payload.get("event_graph") if isinstance(payload.get("event_graph"), dict) else {}
    event_nodes = narrative_graph.get("nodes") if isinstance(narrative_graph, dict) else []
    for node in event_nodes or []:
        if not isinstance(node, dict):
            continue
        actors = node.get("actors") or []
        if isinstance(actors, str):
            actors = [actors]
        if not isinstance(actors, list):
            continue
        for actor in actors:
            if not isinstance(actor, str):
                continue
            name = actor.strip()
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            characters.append(
                {
                    "name": name,
                    "mention_count": 0,
                    "relation_score": 0.0,
                    "confidence": 0.0,
                    "central": False,
                }
            )

    return characters


def _extract_event_index(event_id: Any) -> Optional[int]:
    if not isinstance(event_id, str):
        return None
    candidate = event_id.split(":", 1)[0].strip()
    try:
        return int(candidate)
    except Exception:
        return None


def _extract_actor_events(narrative_graph: Dict[str, Any]) -> Dict[str, Set[int]]:
    actor_events: Dict[str, Set[int]] = {}
    if not isinstance(narrative_graph, dict):
        return actor_events

    for node in narrative_graph.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        node_idx = node.get("idx")
        if not isinstance(node_idx, int):
            continue
        actors = node.get("actors") or []
        if isinstance(actors, str):
            actors = [actors]
        if not isinstance(actors, list):
            continue
        for actor in actors:
            if not isinstance(actor, str):
                continue
            name = actor.strip()
            if not name:
                continue
            actor_events.setdefault(name, set()).add(node_idx)
    return actor_events


def _supported_by_primary_chain(
    character: Dict[str, Any],
    narrative_graph: Dict[str, Any],
    narrative_chains: Dict[str, Any],
) -> bool:
    actor_events = _extract_actor_events(narrative_graph)
    if not isinstance(narrative_chains, dict):
        return False
    chain_confidence = narrative_chains.get("chain_confidence", 0.0)
    chain_count = narrative_chains.get("chain_count", 0)
    if chain_count < 1 or chain_confidence < 0.55:
        return False
    actor_event_ids = actor_events.get(character["name"], set())
    if not actor_event_ids:
        return False

    for chain in narrative_chains.get("chains") or []:
        if not isinstance(chain, dict):
            continue
        for event_label in chain.get("events") or []:
            event_idx = _extract_event_index(event_label)
            if event_idx in actor_event_ids:
                return True
    return False


def _supported_by_cause_effect(
    character: Dict[str, Any],
    narrative_graph: Dict[str, Any],
    cause_effect: Dict[str, Any],
) -> bool:
    actor_events = _extract_actor_events(narrative_graph)
    actor_event_ids = actor_events.get(character["name"], set())
    if not actor_event_ids:
        return False

    relations = cause_effect.get("cause_effect_relations") if isinstance(cause_effect, dict) else []
    for relation in relations or []:
        if not isinstance(relation, dict):
            continue
        cause_idx = _extract_event_index(relation.get("cause_event_id"))
        effect_idx = _extract_event_index(relation.get("effect_event_id"))
        if cause_idx in actor_event_ids or effect_idx in actor_event_ids:
            return True
    return False


def _supported_by_conflict(
    character: Dict[str, Any],
    conflict_graph: Dict[str, Any],
    primary_conflict: Dict[str, Any],
) -> bool:
    if not isinstance(conflict_graph, dict):
        return False
    participants = set()
    for conflict in conflict_graph.get("conflicts") or []:
        if not isinstance(conflict, dict):
            continue
        for participant in conflict.get("participants") or []:
            if isinstance(participant, str):
                participants.add(participant.strip())
    if character["name"] in participants:
        return True

    primary_participants = primary_conflict.get("participants") if isinstance(primary_conflict, dict) else []
    return character["name"] in {p for p in primary_participants if isinstance(p, str)}


def _supported_by_resolution(
    character: Dict[str, Any],
    primary_conflict: Dict[str, Any],
    resolution: Dict[str, Any],
) -> bool:
    if not isinstance(resolution, dict):
        return False
    status = str(resolution.get("status") or "").strip().lower()
    if status not in {"resolved", "partially_resolved"}:
        return False

    primary_participants = primary_conflict.get("participants") if isinstance(primary_conflict, dict) else []
    if character["name"] in {p for p in primary_participants if isinstance(p, str)}:
        return True
    return False


def _compute_character_confidence(character: Dict[str, Any], validation: Dict[str, bool]) -> float:
    character_confidence = _normalize_value_to_float(character.get("confidence") or 0.0)
    support_score = sum(
        1 for key in (
            "supported_by_primary_chain",
            "supported_by_cause_effect",
            "supported_by_conflict",
            "supported_by_resolution",
        )
        if validation.get(key)
    ) / 4.0
    base = support_score * 0.75 + character_confidence * 0.25
    if character.get("mention_count", 0) <= 0 and character.get("relation_score", 0.0) <= 0 and character_confidence <= 0.0:
        base = support_score * 0.5
    return round(min(0.99, base), 2)


def compute_character_validation(
    payload: dict,
    narrative_graph: Dict[str, Any],
    narrative_chains: Dict[str, Any],
    cause_effect: Dict[str, Any],
    conflict_graph: Dict[str, Any],
    primary_conflict: Dict[str, Any],
    resolution: Dict[str, Any],
) -> dict:
    characters = _extract_character_items(payload)
    validations: List[Dict[str, Any]] = []

    for character in characters:
        validation = {
            "supported_by_primary_chain": _supported_by_primary_chain(character, narrative_graph, narrative_chains),
            "supported_by_cause_effect": _supported_by_cause_effect(character, narrative_graph, cause_effect),
            "supported_by_conflict": _supported_by_conflict(character, conflict_graph, primary_conflict),
            "supported_by_resolution": _supported_by_resolution(character, primary_conflict, resolution),
        }
        validation["confidence"] = _compute_character_confidence(character, validation)
        validations.append({"character": character["name"], "validation": validation})

    supported_counts = {
        "validated_character_count": len(validations),
        "primary_chain_character_count": sum(1 for item in validations if item["validation"]["supported_by_primary_chain"]),
        "primary_conflict_character_count": sum(1 for item in validations if item["validation"]["supported_by_conflict"]),
        "resolution_character_count": sum(1 for item in validations if item["validation"]["supported_by_resolution"]),
        "average_character_validation_confidence": round(
            sum(item["validation"]["confidence"] for item in validations) / len(validations),
            2,
        ) if validations else 0.0,
    }

    return {
        "character_validation": validations,
        "diagnostics": supported_counts,
    }
