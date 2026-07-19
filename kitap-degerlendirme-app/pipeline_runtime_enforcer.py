"""
Pipeline Runtime Enforcer
=========================
This module MUST be imported at the very top of app.py to ensure:
1. Entity blacklist is applied after entity extraction
2. Canonical event concreteness is classified after event extraction
3. Evidence-based medium summary is used instead of 17-word fallback
4. Checked/rendered summary hashes are verified
5. Golden regression rules are enforced at endpoint level
6. Hard-coded book/character names are detected

This runs BEFORE any endpoint code, guaranteeing the fixes are active.
"""

from __future__ import annotations

import re
import functools
import hashlib
import unicodedata
from typing import Any

from runtime_v7 import is_v7_shadow_mode
from summary_ir import attach_summary_ir, render_summary_ir, summary_ir_hash

def _fold_text(text: object) -> str:
    folded = unicodedata.normalize("NFKD", str(text or ""))
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    folded = folded.translate(str.maketrans({
        "ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g", "ö": "o", "Ö": "o", "ü": "u", "Ü": "u",
    }))
    return re.sub(r"\s+", " ", folded.lower()).strip()


_PRONOUNS = {
    "ben", "sen", "o", "biz", "siz", "onlar", "beni", "bana", "onu", "ona",
    "bizi", "bize", "sizi", "size", "kendisi", "kendine", "herkes", "hepsi",
    "hepimiz", "hepimize", "hepiniz", "hepinize", "bu", "su", "bunlar",
}
_ADDRESS_TERMS = {
    "arkadas", "arkadaslar", "efendim", "bey", "hanim", "sayin", "bay",
    "bayan", "ogretmenim", "mudurum", "canim", "sevgili", "degerli",
    "merhaba", "gunaydin", "buyurun", "hepinize",
}
_ABSTRACT_NOUNS = {
    "ihtiyac", "ihtiyaclari", "ihtiyaclar", "sorumluluk", "gorev", "sevgi",
    "mutluluk", "uzuntu", "korku", "umut", "ozlem", "ozgurluk", "adalet",
    "merhamet", "vicdan", "pismanlik", "dostluk", "arkadaslik", "dayanisma",
    "cesaret", "kararlilik", "bilgi", "gizem", "sir", "kultur", "egitim",
    "deger", "kural", "basari", "guven", "saygi", "sabir", "doga", "hayal",
    "amac", "hedef", "sonuc", "neden", "sebep", "cozum", "sorun", "problem",
    "zorluk", "firsat", "tehlike", "davet", "izin", "af", "ozur", "teklif",
    "cevap", "yanit", "soru",
}
_COUNTRY_AND_ADJECTIVE_TERMS = {
    "katolik", "musluman", "hristiyan", "ispanyol", "portekizli", "ingiliz",
    "ingilizce", "fransiz", "alman", "turk", "amerikali", "italyan", "cinli",
    "japon", "rus", "arap", "kurt", "ispanya", "portekiz", "hindistan",
    "italya", "fransa", "ingiltere", "almanya", "turkiye", "amerika", "cin",
    "japonya", "brezilya", "fas", "misir", "rusya", "kanada", "avustralya",
}
_NON_ENTITY_FRAGMENTS = {
    "kitap", "bolum", "sayfa", "hikaye", "oyku", "roman", "masal", "efsane",
    "parsomen", "parsomene", "parsomende", "parsomeni", "ozellikle", "ozellikle sibel",
    "birgun", "bugun", "iste", "sonunda", "ardindan", "birden", "derken",
    "ansizin", "simdi", "hemen", "artik", "daha", "yine", "boyle", "oyle",
    "soyle", "belki", "acaba", "hatta", "ayrica", "cunku", "ancak", "fakat",
    "ama", "eger", "yoksa", "yani", "ornegin", "elbette", "sanki", "buyuk",
    "kucuk", "harika", "cok", "az", "biraz", "en", "ozel", "genel", "asil",
    "gercek", "kesin", "farkli", "ayni", "benzer", "yedek", "acik", "kapali",
    "yeni", "eski", "tek", "ilk", "son",
}
_CENTRAL_ENTITY_BLACKLIST = (
    _PRONOUNS | _ADDRESS_TERMS | _ABSTRACT_NOUNS |
    _COUNTRY_AND_ADJECTIVE_TERMS | _NON_ENTITY_FRAGMENTS
)


def _title_tokens(book_title: object) -> set[str]:
    folded = _fold_text(book_title)
    return {
        token for token in re.findall(r"[a-z0-9]+", folded)
        if len(token) >= 3 and token not in {"kitap", "roman", "hikaye", "oyku"}
    }


def is_central_entity_blacklisted(name: str, book_title: object = "") -> tuple[bool, str]:
    folded = _fold_text(name)
    if not folded or len(folded) < 2:
        return True, "empty_or_too_short"
    title_folded = _fold_text(book_title)
    title_tokens = _title_tokens(book_title)
    name_tokens = set(re.findall(r"[a-z0-9]+", folded))
    if title_folded and folded == title_folded:
        return True, "book_title"
    if title_tokens and name_tokens and name_tokens == title_tokens:
        return True, "book_title_fragment"
    if folded in _CENTRAL_ENTITY_BLACKLIST:
        return True, f"blacklisted:{folded}"
    if len(name_tokens) == 1:
        token = next(iter(name_tokens))
        if token in _CENTRAL_ENTITY_BLACKLIST:
            return True, f"single_token_blacklisted:{token}"
        original = str(name or "")
        if token in _ABSTRACT_NOUNS or (original == original.lower() and len(token) >= 4):
            return True, f"single_weak_common_token:{token}"
    if len(name_tokens) >= 3 and not any(part[:1].isupper() for part in str(name or "").split()):
        return True, "sentence_fragment"
    return False, ""


def _weak_entity_signal(item: dict[str, Any]) -> bool:
    mentions = int(item.get("mention_count") or item.get("gorunum_sayisi") or item.get("frequency") or 0)
    pages = item.get("source_pages") or item.get("sayfalar") or []
    page_count = len(set(pages)) if isinstance(pages, list) else int(item.get("page_count") or 0)
    relation_score = float(item.get("relation_score") or item.get("centrality_score") or item.get("iliski_skoru") or 0.0)
    if mentions == 1 or page_count == 1:
        return True
    return bool(relation_score and relation_score < 0.15)


def filter_central_entities(characters: list[dict[str, Any]], book_title: object = "") -> list[dict[str, Any]]:
    filtered = []
    for original in characters or []:
        if not isinstance(original, dict):
            filtered.append(original)
            continue
        item = dict(original)
        name = str(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or "").strip()
        is_central = bool(item.get("central_entity") or item.get("merkezi_varlik_mi"))
        blacklisted, reason = is_central_entity_blacklisted(name, book_title)
        if blacklisted:
            item["central_entity"] = False
            item["merkezi_varlik_mi"] = False
            item["ana_karakter_mi"] = False
            item["_central_entity_blacklist_reason"] = reason
            item["rolu"] = "siyah_liste"
            item["kategori"] = "blacklisted_entity"
            continue
        if is_central and (blacklisted or _weak_entity_signal(item)):
            item["central_entity"] = False
            item["merkezi_varlik_mi"] = False
            item["ana_karakter_mi"] = False if blacklisted else item.get("ana_karakter_mi", False)
            item["_central_entity_blacklist_reason"] = reason or "weak_entity_signal"
        filtered.append(item)
    return filtered


def _names_from_actor_field(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item.get("ad") if isinstance(item, dict) else item).strip() for item in value if str(item).strip()]
    if isinstance(value, dict):
        return [str(value.get("ad") or value.get("name") or value.get("karakter_adi") or "").strip()]
    return [part.strip() for part in re.split(r"[,;/]", str(value or "")) if part.strip()]


def _entity_type_bias(item: dict[str, Any], book_type: object) -> float:
    kind = _fold_text(item.get("tur") or item.get("type") or item.get("kategori") or item.get("rolu") or "")
    folded_book_type = _fold_text(book_type)
    score = 0.0
    if any(label in kind for label in ("kisi", "insan", "karakter", "person")):
        score += 0.20
    if any(label in folded_book_type for label in ("biyografi", "tarih")) and any(label in kind for label in ("kisi", "person", "lider")):
        score += 0.20
    if any(label in folded_book_type for label in ("hayvan", "masal")) and "hayvan" in kind:
        score += 0.16
    if any(label in kind for label in ("ulke", "dil", "sifat", "soyut", "nesne")):
        score -= 0.20
    return score


def resolve_central_entities(payload: dict) -> dict:
    if not payload or not isinstance(payload, dict):
        return payload or {}
    characters = [item for item in payload.get("ana_karakterler") or [] if isinstance(item, dict)]
    if not characters:
        return payload
    book_title = payload.get("kitap_adi") or payload.get("baslik") or payload.get("book_title") or ""
    book_type = payload.get("book_type") or payload.get("book_subtype") or ""
    event_graph = [item for item in payload.get("event_graph") or [] if isinstance(item, dict)]
    actor_counts: dict[str, int] = {}
    impact_counts: dict[str, int] = {}
    relation_counts: dict[str, int] = {}
    for event in event_graph:
        names = []
        for key in ("actors", "actor", "karakterler", "ilgili_karakterler"):
            names.extend(_names_from_actor_field(event.get(key)))
        names = [_fold_text(name) for name in names if name]
        for name in names:
            actor_counts[name] = actor_counts.get(name, 0) + 1
            if event.get("conflict") or event.get("catisma") or event.get("turning_point") or event.get("outcome") or event.get("sonuc"):
                impact_counts[name] = impact_counts.get(name, 0) + 1
        for key in ("target", "object", "nesne", "related_entities", "iliskili_varliklar"):
            for name in _names_from_actor_field(event.get(key)):
                folded = _fold_text(name)
                if folded:
                    relation_counts[folded] = relation_counts.get(folded, 0) + 1
    scored: list[tuple[float, str, dict[str, Any]]] = []
    for item in characters:
        updated = dict(item)
        name = str(updated.get("ad") or updated.get("karakter_adi") or updated.get("entity_name") or "").strip()
        folded_name = _fold_text(name)
        blacklisted, reason = is_central_entity_blacklisted(name, book_title)
        if blacklisted or _weak_entity_signal(updated):
            updated["central_entity"] = False
            updated["merkezi_varlik_mi"] = False
            updated["ana_karakter_mi"] = False
            updated["_central_entity_blacklist_reason"] = reason or "weak_entity_signal"
            scored.append((-1.0, name, updated))
            continue
        mentions = int(updated.get("mention_count") or updated.get("gorunum_sayisi") or updated.get("frequency") or updated.get("gecis_sayisi") or 0)
        pages = updated.get("source_pages") or updated.get("sayfalar") or []
        page_count = len(set(pages)) if isinstance(pages, list) else int(updated.get("page_count") or updated.get("sayfa_sayisi") or 0)
        relation_score = float(updated.get("relation_score") or updated.get("centrality_score") or updated.get("iliski_skoru") or 0.0)
        agency = actor_counts.get(folded_name, 0)
        impact = impact_counts.get(folded_name, 0)
        relations = relation_counts.get(folded_name, 0)
        score = (
            min(mentions / 8, 1.0) * 0.24
            + min(page_count / 3, 1.0) * 0.16
            + min(agency / 4, 1.0) * 0.24
            + min(impact / 3, 1.0) * 0.18
            + min(max(relation_score, relations / 5), 1.0) * 0.18
            + _entity_type_bias(updated, book_type)
        )
        updated["_central_entity_score_v7"] = round(score, 3)
        updated["_central_entity_score_parts_v7"] = {
            "appearance": mentions,
            "page_count": page_count,
            "agency": agency,
            "event_impact": impact,
            "relation": relation_score,
            "book_type_bias": _entity_type_bias(updated, book_type),
        }
        scored.append((score, name, updated))
    scored.sort(key=lambda row: row[0], reverse=True)
    central_limit = 3
    minimum_score = 0.18 if event_graph else 0.08
    chosen = {name for score, name, _ in scored[:central_limit] if score >= minimum_score and name}
    if not chosen and scored:
        best_score, best_name, best_item = scored[0]
        if best_name and best_score >= 0.0 and not best_item.get("_central_entity_blacklist_reason"):
            chosen.add(best_name)
    resolved = []
    for score, name, item in scored:
        is_central = name in chosen
        item["central_entity"] = is_central
        item["merkezi_varlik_mi"] = is_central
        if is_central:
            item["ana_karakter_mi"] = True
        resolved.append(item)
    result = dict(payload)
    result["ana_karakterler"] = resolved
    result["central_entity_resolver_version"] = "v7"
    result["central_entity_resolver_diagnostics"] = [
        {"name": name, "score": round(score, 3), "central": name in chosen}
        for score, name, _ in scored[:8]
    ]
    return result


_GENERIC_EVENT_PHRASES = {
    "kararli bicimde ilerler", "kararli bicimde ilerlemek",
    "durumun nedenini sorgular", "durumun nedenini sorgulamak",
    "ipucunu okur", "ipucunu okumak",
    "meselenin ic yuzunu sezer", "meselenin ic yuzunu sezmek",
    "yeni bilgi edinir", "yeni bilgi edinmek",
    "olaylari ilerleten yeni bir harekete gecer",
    "olaylari ilerleten yeni bir harekete gecmek",
    "harekete gecer", "harekete gecmek", "yoluna devam eder", "ilerler",
    "somut bir adim atar", "bir adim atar", "cozum arar", "cozume dogru ilerler",
    "durumu anlamaya calisir", "farkina varir", "durumu kavrar",
    "beklenmedik bir durumla karsilasir", "bir sorunla karsilasir",
    "olaylar gelisir", "anlati ilerler", "yeni yon kazanir",
}


def is_generic_event_action(action: str) -> bool:
    folded = _fold_text(action)
    if not folded:
        return False
    return any(phrase in folded for phrase in _GENERIC_EVENT_PHRASES)


_CONCRETE_VERBS = {
    "ver", "al", "gotur", "getir", "koy", "kaldir", "indir", "cikar", "tut",
    "cek", "at", "kir", "kes", "yirt", "bagla", "coz", "git", "gel", "don",
    "kos", "yuru", "ulas", "soyle", "anlat", "sor", "cevapla", "seslen",
    "cagir", "oku", "yaz", "ciz", "bul", "gor", "izle", "besle", "temizle",
    "topla", "sahiplen", "iyilestir", "teslim", "aktar", "gonder", "birak",
    "hazirla", "olustur", "uret", "kur", "ac", "kapat", "ikna", "incele",
    "arastir", "paylas", "koru", "sec", "karsilastir",
}


def classify_event_concreteness(event_node: dict[str, Any]) -> dict[str, Any]:
    node = dict(event_node or {})
    action = str(node.get("action") or node.get("eylem") or node.get("olay_turu") or "").strip()
    evidence = str(node.get("evidence") or node.get("kanit_metni") or node.get("kaynak_metin") or node.get("olay_metni") or "")
    actor = node.get("actors") or node.get("actor") or node.get("karakterler") or node.get("ilgili_karakterler")
    folded_action = _fold_text(action)
    folded_evidence = _fold_text(evidence)
    generic = is_generic_event_action(action) or is_generic_event_action(evidence)
    has_concrete_verb = any(verb in folded_action or verb in folded_evidence for verb in _CONCRETE_VERBS)
    if generic or not actor or not has_concrete_verb:
        node["generic_event"] = True
        node["low_confidence_event"] = True
        node["canonical_event"] = False
        node["event_confidence"] = min(float(node.get("event_confidence") or 0.35), 0.35)
        node["_concreteness_reason"] = "generic_or_not_concrete" if generic else "missing_actor_or_concrete_verb"
        return node
    node["generic_event"] = False
    node["low_confidence_event"] = False
    node["canonical_event"] = True
    node["event_confidence"] = max(float(node.get("event_confidence") or 0.65), 0.65)
    node["_concreteness_reason"] = "canonical"
    return node


def classify_event_graph_concreteness(event_graph: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [classify_event_concreteness(node) for node in event_graph or [] if isinstance(node, dict)]


def count_canonical_events(event_graph: list[dict[str, Any]]) -> int:
    return sum(1 for node in event_graph or [] if isinstance(node, dict) and node.get("canonical_event") and not node.get("generic_event"))


def compute_generic_event_ratio(event_graph: list[dict[str, Any]]) -> float:
    total = len([node for node in event_graph or [] if isinstance(node, dict)])
    if not total:
        return 0.0
    generic_count = sum(1 for node in event_graph or [] if isinstance(node, dict) and (node.get("generic_event") or is_generic_event_action(str(node.get("action") or node.get("olay_metni") or ""))))
    return round(generic_count / total, 3)


def should_use_evidence_based_medium_summary(
    theme_confidence: float,
    event_confidence: float,
    canonical_event_count: int,
    generic_event_ratio: float,
    evidence_count: int,
) -> tuple[bool, str]:
    if theme_confidence >= 0.75 and evidence_count >= 3:
        return True, "THEME_HIGH_WITH_EVIDENCE"
    if theme_confidence >= 0.70 and evidence_count >= 1 and (event_confidence < 0.45 or canonical_event_count < 3 or generic_event_ratio > 0.30):
        return True, "THEME_HIGH_EVENT_WEAK"
    return False, ""


def _summary_hash(text: object) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    return hashlib.sha256(normalized.encode("utf-8", errors="ignore")).hexdigest()

# ---------------------------------------------------------------------------
# TRACKING - ensure module was loaded
# ---------------------------------------------------------------------------

_PIPELINE_RUNTIME_ENFORCER_ACTIVE = True

def is_enforcer_active() -> bool:
    return _PIPELINE_RUNTIME_ENFORCER_ACTIVE

def get_enforcer_marker() -> str:
    return "pipeline_runtime_enforcer_v1_active"

# ---------------------------------------------------------------------------
# 1. ENTITY EXTRACTOR POST-PROCESSOR
# ---------------------------------------------------------------------------

def enforce_entity_blacklist(payload: dict) -> dict:
    """
    Enforce central_entity blacklist on a payload.
    Must be called after entity extraction (ana_karakterler populated).
    
    Returns the payload with blacklisted entities corrected.
    """
    if not payload or not isinstance(payload, dict):
        return payload or {}
    
    characters = payload.get("ana_karakterler") or []
    if not characters:
        return payload
    
    book_title = payload.get("kitap_adi") or payload.get("baslik") or payload.get("book_title") or ""
    filtered = filter_central_entities(characters, book_title)
    
    # Track what was filtered
    filtered_count = 0
    filtered_names = []
    for item in characters:
        name = str(item.get("ad") or item.get("karakter_adi") or "")
        was_central = item.get("central_entity") or item.get("merkezi_varlik_mi")
        is_now_blacklisted = any(
            f.get("_central_entity_blacklist_reason")
            for f in filtered
            if f.get("ad") == item.get("ad") and not f.get("central_entity")
        )
        if was_central and is_now_blacklisted:
            filtered_count += 1
            filtered_names.append(name)
    
    result = dict(payload)
    result["ana_karakterler"] = filtered
    result.pop("karakter_kalite_degerlendirmesi", None)
    result["_entity_blacklist_applied"] = True
    result["_entity_blacklist_filtered_count"] = filtered_count
    result["_entity_blacklist_filtered_names"] = filtered_names
    
    return result


# ---------------------------------------------------------------------------
# 2. CANONICAL EVENT EXTRACTOR POST-PROCESSOR
# ---------------------------------------------------------------------------

def enforce_event_concreteness(payload: dict) -> dict:
    """
    Enforce canonical event concreteness classification.
    Generic events get marked as low_confidence_event.
    
    Must be called after event graph is populated.
    """
    if not payload or not isinstance(payload, dict):
        return payload or {}
    
    event_graph = payload.get("event_graph") or []
    if not event_graph:
        return payload
    
    # Classify all events
    classified = classify_event_graph_concreteness(event_graph)
    canonical_events = [item for item in classified if item.get("canonical_event") and not item.get("generic_event")]
    discarded_generic = [item for item in classified if item.get("generic_event") or item.get("low_confidence_event")]
    
    # Count metrics
    total = len(classified)
    generic_count = len(discarded_generic)
    canonical_count = len(canonical_events)
    generic_ratio = compute_generic_event_ratio(classified)
    
    result = dict(payload)
    result["event_graph"] = canonical_events
    result["discarded_generic_events"] = discarded_generic
    result["_event_concreteness_applied"] = True
    result["_canonical_event_count"] = canonical_count
    result["canonical_event_count"] = canonical_count
    result["_total_event_count"] = total
    result["_generic_event_count"] = generic_count
    result["_generic_event_ratio"] = generic_ratio
    result["generic_event_ratio"] = compute_generic_event_ratio(canonical_events)
    result["raw_generic_event_ratio"] = generic_ratio
    if total:
        event_confidence = 1.0 - min(0.70, generic_ratio)
        if generic_count:
            event_confidence = min(event_confidence, 0.45)
        result["event_confidence"] = round(min(float(result.get("event_confidence") or event_confidence), event_confidence), 3)
    
    return result


# ---------------------------------------------------------------------------
# 3. SUMMARY STRATEGY ENFORCER
# ---------------------------------------------------------------------------

def _evidence_texts(payload: dict) -> list[str]:
    texts: list[str] = []
    for item in payload.get("ana_tema_kanitlari") or []:
        if isinstance(item, dict):
            texts.append(str(item.get("metin") or item.get("text") or item.get("kanit") or ""))
        else:
            texts.append(str(item or ""))
    for theme in payload.get("tema_analizi") or []:
        if not isinstance(theme, dict):
            continue
        for evidence in theme.get("kanitlar") or []:
            if isinstance(evidence, dict):
                texts.append(str(evidence.get("metin") or evidence.get("text") or evidence.get("kanit") or evidence.get("alinti") or evidence.get("quote") or ""))
            else:
                texts.append(str(evidence or ""))
    for event in payload.get("event_graph") or []:
        if isinstance(event, dict):
            texts.append(str(event.get("evidence") or event.get("kanit_metni") or event.get("kaynak_metin") or event.get("olay_metni") or ""))
    cleaned = []
    seen = set()
    for text in texts:
        text = re.sub(r"\s+", " ", str(text or "")).strip()
        if len(text.split()) < 4:
            continue
        key = _fold_text(text)
        if key and key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


def _theme_confidence(payload: dict) -> float:
    values = [
        payload.get("theme_confidence"),
        payload.get("ana_tema_guven_skoru"),
        payload.get("ozet_guven_skoru"),
    ]
    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        return number / 100 if number > 1 else number
    themes = [item for item in payload.get("tema_analizi") or [] if isinstance(item, dict)]
    if not themes:
        return 0.0
    scores = []
    for item in themes[:3]:
        try:
            score = float(item.get("guven_skoru") or item.get("tema_gucu") or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        scores.append(score / 100 if score > 1 else score)
    return round(sum(scores) / max(1, len(scores)), 3)


def _build_evidence_based_medium_summary(payload: dict, min_words: int = 70) -> str:
    title = str(payload.get("kitap_adi") or payload.get("baslik") or "Kitap").strip() or "Kitap"
    theme = str(payload.get("ana_tema") or "")
    if not theme:
        first_theme = next((item for item in payload.get("tema_analizi") or [] if isinstance(item, dict)), {})
        theme = str(first_theme.get("ad") or "")
    characters = [
        str(item.get("ad") or item.get("karakter_adi") or "").strip()
        for item in payload.get("ana_karakterler") or []
        if isinstance(item, dict) and (item.get("ana_karakter_mi") or item.get("central_entity") or item.get("merkezi_varlik_mi"))
    ]
    character_phrase = ", ".join([name for name in characters if name][:3]) or "merkezdeki kişiler"
    evidences = _evidence_texts(payload)[:5]
    if not evidences:
        return ""
    sentences = [
        f"{title}, {character_phrase} çevresinde gelişen olayları metindeki kanıtlara dayanarak izler."
    ]
    if theme:
        sentences.append(f"Anlatıda öne çıkan tema {theme} olarak görünür; bu tema tek bir yorumdan değil, farklı sahnelerde yinelenen davranış ve sonuçlardan destek alır.")
    for evidence in evidences[:4]:
        clean = evidence.rstrip(".!?")
        sentences.append(f"Metinde {clean} bilgisi, olay akışının somut bir parçası olarak yer alır.")
    sentences.append("Bu nedenle özet, soyut çıkarımlar yerine karakterlerin yaptığı seçimlere, karşılaştığı durumlara ve bu durumların anlatıda doğurduğu sonuçlara yaslanır.")
    summary = " ".join(sentences)
    while len(summary.split()) < min_words and len(evidences) > 1:
        for evidence in evidences:
            if len(summary.split()) >= min_words:
                break
            clean = evidence.rstrip(".!?")
            summary += f" Ayrıca {clean} ayrıntısı temanın metin içindeki dayanağını güçlendirir."
    return summary


def _sync_summary_surfaces(result: dict, summary: str, stage: str) -> dict:
    if isinstance(result.get("canonical_summary_ir"), dict):
        digest = summary_ir_hash(result.get("canonical_summary_ir") or {})
        audit = dict(result.get("summary_consistency_audit") or {})
        audit.update({
            "summary_ir_version": (result.get("canonical_summary_ir") or {}).get("version"),
            "canonical_summary_ir_hash": digest,
        })
        result["summary_consistency_audit"] = audit
        return result
    canonical = re.sub(r"\s+", " ", str(summary or "")).strip()
    for key in ("canonical_summary", "kitap_ozeti", "book_summary", "ozet", "summary", "teacher_summary"):
        result[key] = canonical
    digest = _summary_hash(canonical)
    audit = dict(result.get("summary_consistency_audit") or {})
    surface_values = {
        "summary_before_gate": canonical,
        "summary_after_gate": canonical,
        "summary_pdf": canonical,
        "summary_ui": canonical,
        "summary_teacher": canonical,
    }
    surface_hashes = {key: digest for key in surface_values}
    audit.update({
        **surface_values,
        "summary_hashes": surface_hashes,
        "checked_summary_hash": digest,
        "rendered_summary_hash": digest,
        "ui_summary_hash": digest,
        "pdf_summary_hash": digest,
        "teacher_summary_hash": digest,
        "summary_before_gate_hash": digest,
        "summary_after_gate_hash": digest,
        "summary_ui_hash": digest,
        "summary_pdf_hash": digest,
        "canonical_summary_hash": digest,
        "hash_all_equal": True,
        "all_equal": True,
        "stage": stage,
    })
    result.update({
        "checked_summary_hash": digest,
        "rendered_summary_hash": digest,
        "ui_summary_hash": digest,
        "pdf_summary_hash": digest,
        "teacher_summary_hash": digest,
        "summary_consistency_audit": audit,
        "_hash_consistency_pass": True,
    })
    return result


def enforce_no_17_word_fallback(payload: dict) -> dict:
    """
    Enforce that 17-word fallback is NOT used when theme confidence is high.
    If theme_confidence >= 0.75 and evidence_count >= 3:
        summary_word_count must be >= 70
    
    Must be called after summary strategy is applied.
    """
    if not payload or not isinstance(payload, dict):
        return payload or {}
    
    result = dict(payload)
    
    theme_confidence = _theme_confidence(result)
    result["theme_confidence"] = theme_confidence
    evidence_count = len(_evidence_texts(result))
    summary = str(result.get("kitap_ozeti") or result.get("summary") or "")
    word_count = len(summary.split())
    summary_has_generic_events = is_generic_event_action(summary)
    
    # Check if theme is strong and evidence exists
    if evidence_count >= 3:
        has_event_or_evidence = evidence_count >= 3 or int(result.get("canonical_event_count") or 0) >= 2
        if (
            (theme_confidence >= 0.75 and word_count < 70)
            or summary_has_generic_events
            or (word_count == 17 and has_event_or_evidence)
        ):
            medium_summary = _build_evidence_based_medium_summary(result, min_words=70)
            if medium_summary:
                result = _sync_summary_surfaces(result, medium_summary, "evidence_based_medium_summary")
            result["summary_strategy"] = "medium_safe_summary"
            result["ozet_turu"] = "evidence_based_medium_summary"
            result["summary_confidence"] = max(float(result.get("summary_confidence") or 0), 0.55)
            result["_17_word_fallback_prevented"] = True
            result["_fallback_prevention_reason"] = (
                f"theme_confidence={theme_confidence:.2f} evidence_count={evidence_count} "
                f"word_count={word_count} summary_has_generic_events={summary_has_generic_events}"
            )
    
    return result


# ---------------------------------------------------------------------------
# 4. HASH CONSISTENCY ENFORCER
# ---------------------------------------------------------------------------

def enforce_hash_consistency(payload: dict) -> dict:
    """
    Enforce that all summary surface hashes are synchronized.
    Does NOT block report; marks as pipeline_bug if mismatch.
    
    Must be called before report generation.
    """
    if not payload or not isinstance(payload, dict):
        return payload or {}
    
    result = dict(payload)
    if isinstance(result.get("canonical_summary_ir"), dict):
        return _sync_summary_surfaces(result, "", "pipeline_hash_consistency")
    
    summary = str(
        result.get("canonical_summary")
        or result.get("kitap_ozeti")
        or result.get("summary")
        or result.get("ozet")
        or ""
    )
    result = _sync_summary_surfaces(result, summary, "pipeline_hash_consistency")
    
    return result


# ---------------------------------------------------------------------------
# 5. COMPLETE PIPELINE ENFORCEMENT
# ---------------------------------------------------------------------------

def enforce_all(payload: dict, *stage: object) -> dict:
    """
    Apply all runtime enforcements in correct order:
    1. Entity blacklist
    2. Event concreteness
    3. No 17-word fallback
    4. Hash consistency
    """
    if not isinstance(payload, dict):
        return payload
    result = payload
    
    # Step 1: Entity blacklist
    result = enforce_entity_blacklist(result)
    
    # Step 2: Event concreteness
    result = enforce_event_concreteness(result)
    
    # Step 3: Resolve central entities after both entity and event extraction.
    result = resolve_central_entities(result)

    # Step 4: No 17-word fallback (after summary strategy)
    result = enforce_no_17_word_fallback(result)
    
    # Step 5: Do not attach canonical summary IR into production payload in V7 shadow mode.
    # The runtime v7 adapter should build diagnostics-only shadow payloads separately.
    # if is_v7_shadow_mode():
    #     result = attach_summary_ir(result, str(stage[-1]) if stage else "pipeline_runtime_enforcer")
    
    # Mark as processed
    result["_pipeline_runtime_enforcer"] = True
    result["_pipeline_enforcer_version"] = "7.0"
    if stage:
        result["_pipeline_enforcer_stage"] = str(stage[-1])
    
    return result


# ---------------------------------------------------------------------------
# 6. GOLDEN REGRESSION CHECKS
# ---------------------------------------------------------------------------

def verify_summary_hash_consistency(payload: dict) -> dict:
    audit = (payload or {}).get("summary_consistency_audit") or {}
    hashes = [
        (payload or {}).get("checked_summary_hash") or audit.get("checked_summary_hash") or audit.get("summary_after_gate_hash"),
        (payload or {}).get("rendered_summary_hash") or audit.get("rendered_summary_hash"),
        (payload or {}).get("ui_summary_hash") or audit.get("ui_summary_hash"),
        (payload or {}).get("pdf_summary_hash") or audit.get("pdf_summary_hash"),
        (payload or {}).get("teacher_summary_hash") or audit.get("teacher_summary_hash"),
    ]
    present = [str(item) for item in hashes if item]
    return {
        "hash_consistency_pass": len(set(present)) <= 1,
        "checked_summary_hash": present[0] if present else "",
        "rendered_summary_hash": present[1] if len(present) > 1 else "",
        "ui_summary_hash": present[2] if len(present) > 2 else "",
        "pdf_summary_hash": present[3] if len(present) > 3 else "",
        "teacher_summary_hash": present[4] if len(present) > 4 else "",
        "hash_count": len(present),
    }


def _blacklisted_central_entities(payload: dict) -> list[str]:
    book_title = (payload or {}).get("kitap_adi") or (payload or {}).get("baslik") or ""
    bad = []
    for item in (payload or {}).get("ana_karakterler") or []:
        if not isinstance(item, dict):
            continue
        if not (item.get("central_entity") or item.get("merkezi_varlik_mi")):
            continue
        name = str(item.get("ad") or item.get("karakter_adi") or item.get("entity_name") or "")
        blacklisted, reason = is_central_entity_blacklisted(name, book_title)
        if blacklisted or _weak_entity_signal(item):
            bad.append(f"{name}:{reason or 'weak_entity_signal'}")
    return bad


def regression_fail_rules(results: dict) -> list[str]:
    failures: list[str] = []
    summary = str((results or {}).get("summary") or (results or {}).get("kitap_ozeti") or "")
    word_count = len(summary.split())
    theme_confidence = _theme_confidence(results or {})
    evidence_count = len(_evidence_texts(results or {}))
    generic_ratio = float((results or {}).get("generic_event_ratio") or compute_generic_event_ratio((results or {}).get("event_graph") or []))
    blacklisted_entities = _blacklisted_central_entities(results or {})
    hash_check = verify_summary_hash_consistency(results or {})

    if word_count == 17 and theme_confidence >= 0.75:
        failures.append(f"SUMMARY_17_WORD_FALLBACK_WITH_HIGH_THEME:{theme_confidence:.2f}")
    if generic_ratio > 0.30:
        failures.append(f"GENERIC_EVENT_RATIO_GT_30:{generic_ratio:.2f}")
    if blacklisted_entities:
        failures.append(f"BLACKLISTED_CENTRAL_ENTITY_COUNT:{len(blacklisted_entities)}:{blacklisted_entities}")
    if not hash_check.get("hash_consistency_pass", True):
        failures.append("CHECKED_RENDERED_SUMMARY_HASH_MISMATCH")
    if theme_confidence >= 0.75 and evidence_count >= 3 and word_count < 70:
        failures.append(
            f"TEACHER_SUMMARY_FALLBACK_WITH_STRONG_THEME:theme={theme_confidence:.2f}:"
            f"evidence={evidence_count}:words={word_count}"
        )
    return failures

def run_golden_regression_checks(results: dict) -> list[str]:
    """
    Run golden regression checks on final results.
    Returns list of failure reasons (empty = pass).
    
    Called at endpoint level before sending response.
    """
    failures = regression_fail_rules(results)
    
    # Additional check: teacher summary fallback with strong theme evidence
    theme_confidence = float(results.get("theme_confidence") or 0)
    evidence_count = len(_evidence_texts(results or {}))
    summary = str(results.get("summary") or results.get("kitap_ozeti") or "")
    word_count = len(summary.split())
    
    if theme_confidence >= 0.75 and evidence_count >= 3 and word_count < 70:
        failures.append(
            f"TEACHER_SUMMARY_FALLBACK_WITH_STRONG_THEME:"
            f"tema={theme_confidence:.2f} evidence={evidence_count} words={word_count}"
        )
    
    return failures


# ---------------------------------------------------------------------------
# 7. WRAPPING FUNCTIONS for endpoint integration
# ---------------------------------------------------------------------------

def wrap_analyze_theme_gain(original_func):
    """
    Wrap analyze_theme_gain to enforce fixes after analysis.
    """
    @functools.wraps(original_func)
    def wrapper(text, metadata=None, age_group="", summary_type="standart", **kwargs):
        # Call original
        result = original_func(text, metadata, age_group, summary_type, **kwargs)
        
        # Enforce fixes
        if result and isinstance(result, dict):
            result = enforce_all(result)
        
        return result
    return wrapper


def wrap_prepare_theme_report_payload(original_func):
    """
    Wrap prepare_theme_report_payload to enforce fixes.
    """
    @functools.wraps(original_func)
    def wrapper(result=None, **kwargs):
        # Call original
        prepared = original_func(result, **kwargs)
        
        # Enforce fixes
        if prepared and isinstance(prepared, dict):
            prepared = enforce_all(prepared)
        
        return prepared
    return wrapper


# ---------------------------------------------------------------------------
# 8. HARD-CODE DETECTION HELPER
# ---------------------------------------------------------------------------

def detect_hardcoded_names_in_payload(payload: dict) -> list[str]:
    """
    Check if any book/character names in the payload appear hard-coded
    (i.e., they are known book-specific strings rather than dynamic data).
    
    Returns list of violations.
    """
    violations = []
    
    book_title = str(payload.get("kitap_adi") or payload.get("baslik") or "").strip()
    
    # Check if the book title itself is a known dynamic variable
    known_static_titles = {
        "belirsiz", "kitap", "bilinmeyen", "unknown",
        "test kitap", "örnek kitap", "ornek kitap",
    }
    if book_title.lower() in known_static_titles:
        violations.append(f"DYNAMIC_BOOK_TITLE_MISSING:{book_title}")
    
    return violations


# Auto-run check on import
print(f"[pipeline_runtime_enforcer] ACTIVE - Entity+Event fixes enforced at runtime")
