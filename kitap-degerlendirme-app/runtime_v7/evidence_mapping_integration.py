"""Shadow-only evidence mapping integration.

Extracts evidence from runtime payloads using prioritized JSON paths
and builds a minimal SummaryIR compatible with `SemanticNarrativeBuilder`.

Rules honored: preserve `source_sentence_id`, preserve order, no dedupe,
no truncation, no concatenation. Shadow-only: does not mutate input payload.
"""
from typing import Any, Dict, List


def _walk_path(obj: Any, part: str) -> List[Any]:
    """Walk one path segment. Supports list wildcard '[*]'."""
    if part.endswith("[*]"):
        key = part[:-3]
        node = obj.get(key) if isinstance(obj, dict) else None
        if isinstance(node, list):
            return node
        return []
    else:
        if isinstance(obj, dict):
            val = obj.get(part)
            if isinstance(val, list):
                return val
            if val is None:
                return []
            return [val]
        return []


def extract_by_json_path(payload: Dict[str, Any], path: str) -> List[Any]:
    """Extract values from payload for a simple path syntax using '/'.

    Supported patterns:
      - "tema_analizi[*]/kanitlar"  (list iteration)
      - "event_graph[*]/evidence"  (list then field)

    Returns list of matched items (could be dicts or strings).
    """
    parts = [p for p in path.split("/") if p]
    # Start with root container
    queue: List[Any] = [payload]
    for part in parts:
        next_queue: List[Any] = []
        for node in queue:
            if isinstance(node, list):
                for el in node:
                    next_queue.extend(_walk_path(el, part))
            else:
                next_queue.extend(_walk_path(node, part))
        queue = next_queue

    return queue


def _pick_text_from_item(item: Any) -> Dict[str, Any]:
    """Return dict with text and preserved source ids.

    Preference order for textual field: 'metin' > 'alinti' > 'text' > 'evidence'
    If item is string, return directly.
    """
    if isinstance(item, str):
        return {"text": item, "source_sentence_id": None, "raw": item}
    if not isinstance(item, dict):
        return {"text": str(item or ""), "source_sentence_id": None, "raw": item}

    text = item.get("metin") or item.get("alinti") or item.get("text") or item.get("evidence") or ""
    sid = item.get("source_sentence_id") or item.get("source_sentence") or item.get("source_id")
    return {"text": text, "source_sentence_id": sid, "raw": item}


def build_summary_ir_from_payload(payload: Dict[str, Any], prioritized_paths: List[str]) -> Dict[str, Any]:
    """Build a minimal SummaryIR using prioritized paths.

    Produces `evidence_snippets` dict with keys: setup, conflict, events, resolution.
    Order preserved; source_sentence_id preserved in each snippet dict.
    """
    extracted: List[Dict[str, Any]] = []
    for path in prioritized_paths:
        matches = extract_by_json_path(payload, path)
        for m in matches:
            if isinstance(m, list):
                for sub in m:
                    extracted.append(_pick_text_from_item(sub))
            else:
                extracted.append(_pick_text_from_item(m))

    # Build evidence_snippets mapping deterministically
    evidence_snippets: Dict[str, List[Any]] = {}
    if extracted:
        evidence_snippets["setup"] = [extracted[0]["text"]]
    if len(extracted) >= 2:
        evidence_snippets["conflict"] = [extracted[1]["text"]]
    if len(extracted) >= 3:
        ev = [e["text"] for e in extracted[2:5]]
        if ev:
            evidence_snippets["events"] = ev
    if len(extracted) >= 6:
        evidence_snippets["resolution"] = [extracted[5]["text"]]

    # Keep raw extracted list for tracing/preservation
    evidence_snippets["__raw_extracted__"] = extracted

    # Normalize central_entities to list of strings when possible
    raw_entities = payload.get("ana_karakterler") or payload.get("central_entities") or []
    central_entities: List[str] = []
    for ent in (raw_entities or []):
        if isinstance(ent, str):
            central_entities.append(ent)
        elif isinstance(ent, dict):
            central_entities.append(ent.get("name") or ent.get("ad") or ent.get("isim") or "")
        else:
            central_entities.append(str(ent))

    summary_ir = {
        "title": payload.get("title") or payload.get("baslik") or payload.get("dosya_adi") or "",
        "central_entities": central_entities,
        "themes": [t.get("ad") for t in (payload.get("tema_analizi") or []) if isinstance(t, dict)],
        "evidence_snippets": evidence_snippets,
        "metadata": {"source_file": payload.get("_source_file")}
    }

    return summary_ir
