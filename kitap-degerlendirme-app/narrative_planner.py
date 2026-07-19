from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Any


NARRATIVE_PLAN_SCHEMAS = {
    "fiction_story": ["baslangic", "catisma", "gelisme", "cozum_arayisi", "sonuc"],
    "fantasy_story": ["baslangic", "catisma", "gelisme", "cozum_arayisi", "sonuc"],
    "fairy_tale": ["masal_duzeni", "eksiklik_veya_dilek", "deneme", "yardimci_unsur", "ders_sonuc"],
    "historical_biography": ["amac_merak", "hazirlik", "girisimler", "engeller", "sonuc_tarihsel_etki"],
    "daily_life_story": ["gundelik_durum", "sorun", "karakterin_tepkisi", "iliski_sorumluluk", "sonuc"],
    "animal_responsibility_story": ["hayvanla_karsilasma", "sahiplenme_bakim", "sorun", "sorumluluk_farkindaligi", "cozum"],
    "information_book": ["ana_kavram", "aciklama", "ornekler", "bilgi_iliskileri", "ogrenme_sonucu"],
    "memoir": ["hatirlama_noktasi", "gecmis_durum", "degisim", "duygusal_farkindalik", "sonuc"],
    "poem_or_symbolic_text": ["ana_imge", "duygu", "tekrar_motif", "yorum", "sonuc"],
    "multiple_story_collection": ["cerceve", "oyku_odaklari", "ortak_tema", "degisen_durumlar", "genel_sonuc"],
}


@dataclass(frozen=True)
class NarrativePlan:
    narrative_type: str
    stages: list[str]
    strategy_hint: str


NARRATIVE_OUTLINE_STAGES = [
    "introduction",
    "initial_state",
    "inciting_incident",
    "rising_events",
    "turning_point",
    "resolution",
    "closing",
]


SYSTEM_LABELS_FOLDED = {
    "bu okuma",
    "sonuc olarak",
    "olay akisi",
    "somut bir karar uygulamak",
    "cozume yarayan bilgi bulmak",
    "cozum yolunu anlamak",
    "sahnedeki sorun veya ipucu",
    "onceki sahnedeki bilgi",
    "karabasan sorununa karsi cozum arayisi belirginlesir",
    "bilgi veya nesne baska bir kisiye aktarilir",
    "sahne yeni bir yere veya karara yonelir",
}


def _fold_text(text: object) -> str:
    folded = unicodedata.normalize("NFKD", str(text or ""))
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", folded.lower()).strip()


def _clean(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _first_text(node: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = _clean(node.get(key))
        if value:
            return value
    return ""


def _actor_names(node: dict[str, Any]) -> list[str]:
    values = node.get("actors") or node.get("karakterler") or node.get("ilgili_karakterler") or []
    if isinstance(values, str):
        names = [part.strip() for part in re.split(r"[,;/]", values) if part.strip()]
    elif isinstance(values, list):
        names = [_clean(item.get("ad") if isinstance(item, dict) else item) for item in values]
    else:
        names = []
    actor = _clean(node.get("actor"))
    if actor:
        names.insert(0, actor)
    return [name for name in dict.fromkeys(names) if name][:3]


def _join_names(names: list[str]) -> str:
    names = [name for name in names if name]
    if not names:
        return "karakterler"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} ve {names[1]}"
    return ", ".join(names[:-1]) + f" ve {names[-1]}"


def _is_system_text(text: object) -> bool:
    folded = _fold_text(text)
    return any(label in folded for label in SYSTEM_LABELS_FOLDED)


def _natural_action(action: object) -> str:
    folded = _fold_text(action)
    if not folded or _is_system_text(action):
        return ""
    replacements = {
        "sorumluluk almak": "sorumluluk üstlenir",
        "bilgi aktarmak": "bildiklerini paylaşır",
        "yardim etmek": "yardım eder",
        "yardım etmek": "yardım eder",
        "karar vermek": "karar verir",
        "korumak": "korumaya çalışır",
        "aramak": "arar",
        "bulmak": "bulur",
        "gitmek": "gider",
        "hazirlamak": "hazırlar",
        "hazırlamak": "hazırlar",
        "anlatmak": "anlatır",
        "paylasmak": "paylaşır",
        "paylaşmak": "paylaşır",
    }
    for needle, replacement in replacements.items():
        if needle in folded:
            return replacement
    text = _clean(action)
    if len(text.split()) <= 6:
        return text
    return ""


def _strip_actor_from_action(actor: str, action: str) -> str:
    actor = _clean(actor)
    action = _clean(action)
    if not actor or not action:
        return action
    if action.startswith(actor + " "):
        return action[len(actor) + 1 :].strip()
    if action.lower().startswith(actor.lower() + " "):
        return action[len(actor) + 1 :].strip()
    return action


def _event_summary(node: dict[str, Any]) -> str:
    actors = _join_names(_actor_names(node))
    raw_action = node.get("action") or node.get("eylem") or ""
    action = _natural_action(_strip_actor_from_action(actors, raw_action))
    conflict = _first_text(node, ("conflict", "catisma", "obstacle", "engel", "problem"))
    outcome = _first_text(node, ("resolution", "cozum", "outcome", "sonuc", "consequence"))
    if _is_system_text(conflict):
        conflict = ""
    if _is_system_text(outcome):
        outcome = ""
    if conflict and action and outcome:
        return f"{actors}, {conflict.lower()} karşısında {action}; bu adımın ardından {outcome.lower()}."
    if conflict and action:
        return f"{actors}, {conflict.lower()} karşısında {action}."
    if action and outcome:
        return f"{actors} {action}; bu adım anlatıdaki dengeleri değiştirir ve {outcome.lower()}."
    if action:
        return f"{actors} {action}."
    if conflict:
        return f"{actors}, {conflict.lower()} ile karşı karşıya kalır."
    if outcome:
        return f"{actors} açısından yeni bir sonuç doğar: {outcome}."
    return ""


def event_importance_score(node: dict[str, Any]) -> float:
    score = 0.15
    text_blob = _fold_text(" ".join(str(node.get(key) or "") for key in (
        "olay_turu", "phase", "conflict", "catisma", "obstacle", "turning_point",
        "donum_noktasi", "resolution", "cozum", "outcome", "sonuc", "consequence",
        "action", "evidence",
    )))
    if any(key in text_blob for key in ("turning", "donum", "dönüm", "kirilm", "kırılm")):
        score += 0.35
    if any(key in text_blob for key in ("conflict", "catisma", "çatışma", "engel", "sorun", "tehlike")):
        score += 0.25
    if any(key in text_blob for key in ("resolution", "cozum", "çözüm", "sonuc", "kapan", "iyiles", "başar")):
        score += 0.25
    if node.get("canonical_event"):
        score += 0.10
    if node.get("generic_event") or _is_system_text(node.get("action")):
        score -= 0.25
    if node.get("merged_event_count"):
        try:
            score += min(float(node.get("merged_event_count")) / 10, 0.12)
        except (TypeError, ValueError):
            pass
    return round(max(0.0, min(score, 1.0)), 3)


def _dedupe_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for event in events:
        actors = ",".join(_actor_names(event))
        action = _fold_text(event.get("action") or event.get("eylem"))
        key = (actors.casefold(), action[:32])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)
    return deduped


def build_narrative_outline(payload: dict) -> dict:
    payload = payload or {}
    title = _clean(payload.get("kitap_adi") or payload.get("baslik") or payload.get("book_title") or "Kitap")
    central_entities = [
        _clean(item.get("ad") or item.get("karakter_adi") or item.get("entity_name"))
        for item in _as_list(payload.get("ana_karakterler"))
        if isinstance(item, dict) and (item.get("central_entity") or item.get("merkezi_varlik_mi") or item.get("ana_karakter_mi"))
    ]
    central_entities = [item for item in dict.fromkeys(central_entities) if item][:4]
    raw_events = [
        dict(item)
        for item in _as_list(payload.get("event_graph"))
        if isinstance(item, dict) and item.get("canonical_event") and not item.get("generic_event")
    ]
    for index, event in enumerate(raw_events):
        event["_sequence_index"] = index
        event["event_importance"] = event_importance_score(event)
        event["natural_summary"] = _event_summary(event)
    events = _dedupe_events([event for event in raw_events if event.get("natural_summary")])
    events_by_importance = sorted(events, key=lambda item: (item.get("event_importance", 0), -item.get("_sequence_index", 0)), reverse=True)
    high = [event for event in events_by_importance if float(event.get("event_importance") or 0) >= 0.45]
    selected = sorted(_dedupe_events(high[:5] + events[:4]), key=lambda item: item.get("_sequence_index", 0))[:6]
    intro_people = _join_names(central_entities)
    themes = [
        _clean(item.get("ad") or item.get("tema") or item.get("name"))
        for item in _as_list(payload.get("ilk_uc_baskin_tema") or payload.get("tema_analizi"))
        if isinstance(item, dict)
    ][:3]
    introduction = f"{title}, {intro_people} çevresinde gelişen bir anlatıdır."
    if themes:
        introduction += f" Hikaye {', '.join(themes)} temalarıyla derinleşir."
    initial = selected[0]["natural_summary"] if selected else f"{intro_people}, hikayenin başında kendi düzeni içinde görünür."
    inciting = ""
    for event in selected:
        if float(event.get("event_importance") or 0) >= 0.35:
            inciting = event["natural_summary"]
            break
    if not inciting and len(selected) > 1:
        inciting = selected[1]["natural_summary"]
    rising = [event["natural_summary"] for event in selected[1:4] if event.get("natural_summary")]
    turning_event = next((event for event in events_by_importance if float(event.get("event_importance") or 0) >= 0.55), None)
    turning = (turning_event or (selected[-2] if len(selected) >= 2 else None) or (selected[-1] if selected else None))
    resolution_event = next(
        (
            event for event in reversed(selected)
            if any(key in _fold_text(" ".join(str(event.get(field) or "") for field in ("resolution", "cozum", "outcome", "sonuc", "consequence"))) for key in ("cozum", "çözüm", "sonuc", "kapan", "iyiles"))
        ),
        selected[-1] if selected else None,
    )
    resolution = resolution_event["natural_summary"] if resolution_event else f"{intro_people}, yaşananlardan sonra yeni bir dengeye ulaşır."
    closing = f"Böylece {title}, karakterlerin seçimleriyle başlayan gerilimi daha açık bir sonuca bağlar."
    outline = {
        "introduction": introduction,
        "initial_state": initial,
        "inciting_incident": inciting or initial,
        "rising_events": rising,
        "turning_point": turning["natural_summary"] if turning else "",
        "resolution": resolution,
        "closing": closing,
    }
    return {
        "version": "narrative-outline-v1",
        "stages": NARRATIVE_OUTLINE_STAGES,
        "outline": outline,
        "event_sequence": [
            {
                "index": event.get("_sequence_index"),
                "actors": _actor_names(event),
                "importance": event.get("event_importance"),
                "summary": event.get("natural_summary"),
                "conflict": _first_text(event, ("conflict", "catisma", "obstacle", "engel", "problem")),
                "outcome": _first_text(event, ("resolution", "cozum", "outcome", "sonuc", "consequence")),
                "turning_point": _first_text(event, ("turning_point", "donum_noktasi", "donum", "kirilma", "dönüm")),
                **({
                    "source_sentence_id": event.get("source_sentence_id"),
                    "source_sentence_ids": event.get("source_sentence_ids"),
                } if (event.get("source_sentence_id") or event.get("source_sentence_ids")) else {})
            }
            for event in selected
        ],
        "event_importance": [
            {
                "index": event.get("_sequence_index"),
                "actors": _actor_names(event),
                "importance": event.get("event_importance"),
                "selected": event in selected,
                **({
                    "source_sentence_id": event.get("source_sentence_id"),
                    "source_sentence_ids": event.get("source_sentence_ids"),
                } if (event.get("source_sentence_id") or event.get("source_sentence_ids")) else {})
            }
            for event in raw_events
        ],
        "turning_points": [
            {
                "natural_summary": turning["natural_summary"],
                **({"source_sentence_id": turning.get("source_sentence_id")} if turning.get("source_sentence_id") else {}),
                **({"source_sentence_ids": turning.get("source_sentence_ids")} if turning.get("source_sentence_ids") else {}),
            } if turning else {}
        ] if turning else [],
        "resolution": resolution,
    }


def build_narrative_plan(narrative_type: str, event_count: int = 0) -> NarrativePlan:
    normalized = narrative_type if narrative_type in NARRATIVE_PLAN_SCHEMAS else "fiction_story"
    stages = list(NARRATIVE_PLAN_SCHEMAS[normalized])
    if normalized == "information_book":
        hint = "conceptual"
    elif event_count and event_count < 4:
        hint = "short_safe"
    else:
        hint = "event_chronology"
    return NarrativePlan(normalized, stages, hint)


def attach_narrative_plan(payload: dict) -> dict:
    updated = dict(payload or {})
    plan = build_narrative_plan(
        str(updated.get("narrative_type") or "fiction_story"),
        len(updated.get("event_graph") or []),
    )
    updated["narrative_plan"] = {
        "narrative_type": plan.narrative_type,
        "stages": plan.stages,
        "strategy_hint": plan.strategy_hint,
    }
    return updated
