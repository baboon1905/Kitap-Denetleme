from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from datetime import datetime
from typing import Any

from narrative_planner import build_narrative_outline
from narrative_realizer import realize_narrative_outline


SUMMARY_IR_VERSION = "summary-ir-v7-phase1"
FORBIDDEN_RENDER_MARKERS = [
    "Bu okuma",
    "Sonuç olarak",
    "Sonuc olarak",
    "Olay akışı",
    "Olay akisi",
    "somut bir karar uygulamak",
    "çözüme yarayan bilgi bulmak",
    "cozume yarayan bilgi bulmak",
    # Pipeline expression markers from quality gate
    "Olay adımı",
    "Olay zincirinde",
    "Başlangıç durumu",
    "Önceki olayda ortaya çıkan durum",
    "Çatışmanın belirginleşmesi",
    "anlatı ilerler",
    "yeni yön kazanır",
    "bu aşamada",
    "olaylar gelişir",
    "karakter harekete geçer",
    "olay zinciri",
    "sahnedeki sorun veya ipucu",
    "önemli bilgi",
    "somut bir adım",
    "çözüm için harekete geçer",
    "durumu daha iyi anlar",
    "önceki gelişmenin ardından",
    "önceki sahnedeki bilgi",
    "önemli bulmasını paylaşır",
    "çözüm yolunu başlatır",
    "olayın anlamını kavrar",
    "bu gelişmeden sonra",
    "önemli bir ipucu",
    "bilgi veya nesne başka bir kişiye aktarılır",
    "sahnedeki belirsizlik",
    "sahnedeki sorun",
    "daha önce öğrenilenler",
    "sahne yeni bir yere veya karara yönelir",
    "belirleyici bir iz",
    "onemli bir ipucu",
    "cozum icin kullanilabilecek bilgi ortaya cikar",
    "karabasan sorununa karsi cozum arayisi belirginlesir",
    "onemli bulusunu paylasir",
    "cozum yolunu baslatir",
    "olayin anlamini kavrar",
    "bu gelismeden sonra",
    "onceki sahnedeki bilgi",
    "daha once ogrenilenler",
    "bu adım",
    "anlatıdaki",
    "anlatıda",
    "dengeleri değiştirir",
    "bu adım anlatıdaki dengeleri değiştirir",
    "bu adım anlatıda dengeleri değiştirir",
    "sahnedeki sorun",
    "sahnedeki belirsizlik",
    "olaylar gelişir",
    "karakter harekete geçer",
    "anlatı ilerler",
    "yeni yön kazanır",
    "başlangıç durumu",
    "ö nceki olayda ortaya çıkan durum",
    "çözüm için harekete geçer",
    "onemli bilgi",
]


def _clean(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _log_sanitization(removed: list[str], original: str, cleaned: str) -> None:
    try:
        with open(os.path.abspath("debug_summary_ir_sanitization.log"), "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.now().isoformat()} removed={removed} original={original[:300]!r} cleaned={cleaned[:300]!r}\n"
            )
    except Exception:
        pass


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _normalize_source_ids(value: Any) -> list[str]:
    """
    Extract and normalize source IDs from various field formats.
    
    Supports:
    - source_sentence_id: "p14:s4" -> ["p14:s4"]
    - source_sentence_ids: ["p14:s4", "p15:s2"] -> ["p14:s4", "p15:s2"]
    - source_ids: [...] -> [...]
    - sentence_ids: [...] -> [...]
    - evidence_ids: [...] -> [...]
    
    Returns list[str] with duplicates removed (preserving first occurrence order).
    Never mutates input.
    """
    result = []
    seen = set()
    
    if isinstance(value, str) and value.strip():
        # Singular string ID
        clean_val = str(value).strip()
        if clean_val and clean_val not in seen:
            result.append(clean_val)
            seen.add(clean_val)
    elif isinstance(value, (list, tuple)):
        # Already a list/tuple
        for item in value:
            if isinstance(item, str) and item.strip():
                clean_val = str(item).strip()
                if clean_val and clean_val not in seen:
                    result.append(clean_val)
                    seen.add(clean_val)
            elif isinstance(item, (int, float)) and not isinstance(item, bool):
                clean_val = str(int(item))
                if clean_val and clean_val not in seen:
                    result.append(clean_val)
                    seen.add(clean_val)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        # Single numeric ID
        clean_val = str(int(value))
        if clean_val and clean_val not in seen:
            result.append(clean_val)
            seen.add(clean_val)
    
    return result


def _normalize_item_source_ids(item: Any) -> Any:
    """
    Recursively normalize source ID fields in an item (dict, list, or scalar).
    
    For dicts: extracts source IDs from singular/plural fields and normalizes to plural.
    For lists: recursively normalizes each element.
    For scalars: returns unchanged.
    
    Never mutates input; returns normalized copy.
    """
    if isinstance(item, dict):
        # Create shallow copy to avoid mutation
        normalized = dict(item)
        
        # Check for any source ID field and normalize
        for singular_key in ("source_sentence_id", "source_id", "sentence_id", "evidence_id", "kanit_id"):
            if singular_key in normalized:
                ids = _normalize_source_ids(normalized.pop(singular_key))
                if ids:
                    normalized["source_sentence_ids"] = ids
                break
        
        # Also check plural forms and normalize them
        for plural_key in ("source_sentence_ids", "source_ids", "sentence_ids", "evidence_ids"):
            if plural_key in normalized:
                ids = _normalize_source_ids(normalized.pop(plural_key))
                if ids:
                    normalized["source_sentence_ids"] = ids
                break
        
        # Recursively normalize nested lists/dicts
        for key, value in list(normalized.items()):
            if isinstance(value, list):
                normalized[key] = [_normalize_item_source_ids(v) for v in value]
            elif isinstance(value, dict):
                normalized[key] = _normalize_item_source_ids(value)
        
        return normalized
    elif isinstance(item, (list, tuple)):
        # Recursively normalize list items
        return [_normalize_item_source_ids(v) for v in item]
    else:
        # Return scalars unchanged
        return item


def _hash_object(value: object) -> str:
    import json

    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def _entity_name(item: object) -> str:
    if isinstance(item, dict):
        return _clean(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or item.get("name"))
    return _clean(item)


def _event_text(item: object) -> str:
    if isinstance(item, dict):
        parts = [
            item.get("summary"),
            item.get("olay_metni"),
            item.get("action"),
            item.get("eylem"),
            item.get("evidence"),
            item.get("kanit_metni"),
            item.get("kaynak_metin"),
        ]
        for part in parts:
            text = _clean(part)
            if len(text.split()) >= 4:
                return text.rstrip(".!?") + "."
    return _clean(item)


def _fold_ascii(text: object) -> str:
    folded = unicodedata.normalize("NFKC", str(text or ""))
    translation = str.maketrans({
        "ç": "c",
        "Ç": "C",
        "ğ": "g",
        "Ğ": "G",
        "ı": "i",
        "İ": "I",
        "ö": "o",
        "Ö": "O",
        "ş": "s",
        "Ş": "S",
        "ü": "u",
        "Ü": "U",
    })
    return folded.translate(translation)


def _sanitize_rendered_summary(text: object) -> str:
    cleaned = _clean(text)
    cleaned_folded = _fold_ascii(cleaned).lower()
    removed = []
    for marker in FORBIDDEN_RENDER_MARKERS:
        marker_folded = _fold_ascii(marker).lower()
        if not marker_folded:
            continue
        pattern = re.compile(re.escape(marker_folded), flags=re.IGNORECASE)
        while True:
            match = pattern.search(cleaned_folded)
            if not match:
                break
            start, end = match.span()
            cleaned = cleaned[:start] + cleaned[end:]
            cleaned_folded = cleaned_folded[:start] + cleaned_folded[end:]
            removed.append(marker)
    cleaned = re.sub(r"\bve\s*\.\s*", ".", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[;:,]\s*\.\s*", ".", cleaned)
    cleaned = re.sub(r"\s+([?.!,;:])", r"\1", cleaned)
    cleaned = _clean(cleaned)
    if removed:
        _log_sanitization(removed, str(text), cleaned)
    return cleaned


def _theme_name(item: object) -> str:
    if isinstance(item, dict):
        return _clean(item.get("ad") or item.get("tema") or item.get("name") or item.get("label"))
    return _clean(item)


def _evidence_text(item: object) -> str:
    if isinstance(item, dict):
        return _clean(
            item.get("metin")
            or item.get("text")
            or item.get("kanit")
            or item.get("alinti")
            or item.get("quote")
            or item.get("cumle")
        )
    return _clean(item)


def collect_summary_evidence(payload: dict) -> list:
    """Collect evidence items with text and source ID preservation."""
    evidence: list = []
    for item in _as_list((payload or {}).get("ana_tema_kanitlari")):
        text = _evidence_text(item)
        if len(text.split()) >= 4:
            # Preserve item as dict with text and source IDs
            ev = {"text": text}
            if isinstance(item, dict):
                # Preserve source ID fields if present
                if item.get("source_sentence_id"):
                    ev["source_sentence_id"] = item["source_sentence_id"]
                if item.get("source_sentence_ids"):
                    ev["source_sentence_ids"] = item["source_sentence_ids"]
            evidence.append(ev)
    
    for theme in _as_list((payload or {}).get("tema_analizi")):
        if not isinstance(theme, dict):
            continue
        for item in _as_list(theme.get("kanitlar")):
            text = _evidence_text(item)
            if len(text.split()) >= 4:
                # Preserve item as dict with text and source IDs
                ev = {"text": text}
                if isinstance(item, dict):
                    # Preserve source ID fields if present
                    if item.get("source_sentence_id"):
                        ev["source_sentence_id"] = item["source_sentence_id"]
                    if item.get("source_sentence_ids"):
                        ev["source_sentence_ids"] = item["source_sentence_ids"]
                evidence.append(ev)
    
    for event in _as_list((payload or {}).get("event_graph")):
        text = _event_text(event)
        if len(text.split()) >= 4:
            # Preserve item as dict with text and source IDs
            ev = {"text": text}
            if isinstance(event, dict):
                # Preserve source ID fields if present
                if event.get("source_sentence_id"):
                    ev["source_sentence_id"] = event["source_sentence_id"]
                if event.get("source_sentence_ids"):
                    ev["source_sentence_ids"] = event["source_sentence_ids"]
            evidence.append(ev)
    
    # Deduplicate by text
    seen: set[str] = set()
    clean: list = []
    for item in evidence:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        key = text.casefold()
        if key not in seen:
            seen.add(key)
            clean.append(item)
    
    return clean[:12]


def build_summary_ir(payload: dict) -> dict:
    payload = payload or {}
    narrative_outline = build_narrative_outline(payload)
    outline = narrative_outline.get("outline") or {}
    central_entities = [
        _entity_name(item)
        for item in _as_list(payload.get("ana_karakterler"))
        if isinstance(item, dict) and (item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi"))
    ]
    central_entities = [item for item in dict.fromkeys(central_entities) if item][:4]
    evidence = collect_summary_evidence(payload)
    themes = [_theme_name(item) for item in _as_list(payload.get("ilk_uc_baskin_tema") or payload.get("tema_analizi"))]
    themes = [item for item in dict.fromkeys(themes) if item][:5]
    confidence = {
        "theme": payload.get("theme_confidence") or payload.get("ana_tema_guven_skoru") or payload.get("ozet_guven_skoru") or 0,
        "summary": payload.get("summary_confidence") or payload.get("ozet_guven_skoru") or 0,
        "event": payload.get("event_confidence") or 0,
        "entity": payload.get("entity_confidence") or 0,
    }
    def _entity_summary(item: dict) -> dict:
        return {
            "name": _entity_name(item),
            "type": str(item.get("entity_type") or item.get("tur") or item.get("type") or "").strip(),
            "central": bool(item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi")),
            "mention_count": int(item.get("mention_count") or item.get("gorunum_sayisi") or item.get("frequency") or 0),
            "source_pages": item.get("source_pages") or item.get("sayfalar") or [],
            "relation_score": float(item.get("relation_score") or item.get("centrality_score") or item.get("iliski_skoru") or 0.0),
        }
    entity_graph_summary = [
        _entity_summary(item)
        for item in _as_list(payload.get("ana_karakterler"))
        if isinstance(item, dict) and _entity_name(item)
    ][:8]
    event_sequence = _as_list(narrative_outline.get("event_sequence"))
    narrative_graph = {
        "nodes": [
            {
                "index": item.get("index"),
                "actors": item.get("actors") or [],
                "summary": _clean(item.get("summary")),
                "importance": item.get("importance"),
                "conflict": item.get("conflict"),
                "outcome": item.get("outcome"),
            }
            for item in event_sequence
            if isinstance(item, dict)
        ],
        "edges": [
            {"source": idx, "target": idx + 1, "relation": "sequential"}
            for idx in range(max(0, len(event_sequence) - 1))
        ],
    }
    ir = {
        "version": SUMMARY_IR_VERSION,
        "introduction": _clean(outline.get("introduction")),
        "initial_state": _clean(outline.get("initial_state")),
        "inciting_incident": _clean(outline.get("inciting_incident")),
        "rising_events": [_clean(item) for item in _as_list(outline.get("rising_events")) if _clean(item)],
        "closing": _clean(outline.get("closing")),
        "central_entities": central_entities,
        "entity_graph_summary": entity_graph_summary,
        "narrative_graph": narrative_graph,
        "timeline": [_clean(item.get("summary")) for item in event_sequence if isinstance(item, dict) and _clean(item.get("summary"))],
        "story_arc": narrative_outline,
        "event_sequence": event_sequence,
        "turning_points": narrative_outline.get("turning_points") or [],
        "resolution": narrative_outline.get("resolution") or _clean(outline.get("resolution")),
        "event_importance": narrative_outline.get("event_importance") or [],
        "themes": themes,
        "evidence": evidence[:8],
        "confidence": confidence,
        "diagnostics": {
            "source": "runtime_v7_phase1_narrative_planner",
            "event_count": len(event_sequence),
            "evidence_count": len(evidence),
            "central_entity_count": len(central_entities),
            "summary_generation": "canonical_event_graph_to_outline_to_surface",
        },
    }
    
    # Normalize source IDs in target fields (canonical IR only, never mutates upstream payload)
    for target_field in ("event_sequence", "turning_points", "event_importance", "resolution", "narrative_graph"):
        if target_field in ir:
            ir[target_field] = _normalize_item_source_ids(ir[target_field])
    
    ir["hash"] = _hash_object({key: value for key, value in ir.items() if key != "hash"})
    return ir


def summary_ir_hash(summary_ir: dict) -> str:
    if isinstance(summary_ir, dict) and summary_ir.get("hash"):
        return str(summary_ir.get("hash"))
    return _hash_object(summary_ir or {})


def render_summary_ir(summary_ir: dict, surface: str = "ui", min_words: int = 70) -> str:
    ir = summary_ir or {}
    story_arc = ir.get("story_arc") or {
        "outline": {
            "introduction": ir.get("introduction"),
            "initial_state": ir.get("initial_state"),
            "inciting_incident": ir.get("inciting_incident"),
            "rising_events": ir.get("rising_events") or [],
            "turning_point": (ir.get("turning_points") or [""])[0] if isinstance(ir.get("turning_points"), list) else "",
            "resolution": ir.get("resolution"),
            "closing": ir.get("closing"),
        }
    }
    summary = realize_narrative_outline(story_arc, min_words=max(min_words, 90), max_words=180)
    return _sanitize_rendered_summary(summary)


def attach_summary_ir(payload: dict, stage: str = "") -> dict:
    result = dict(payload or {})
    summary_ir = build_summary_ir(result)
    result["canonical_summary_ir"] = summary_ir
    digest = summary_ir_hash(summary_ir)
    result["canonical_summary_ir_hash"] = digest
    audit = dict(result.get("summary_consistency_audit") or {})
    audit.update({
        "summary_ir_version": SUMMARY_IR_VERSION,
        "canonical_summary_ir_hash": digest,
    })
    result["summary_consistency_audit"] = audit
    return result
