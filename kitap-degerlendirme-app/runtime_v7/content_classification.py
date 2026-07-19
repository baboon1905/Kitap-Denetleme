from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from runtime_v7.constants.semantic_patterns import (
    CONTENT_LABEL_REALISTIC_STORY,
    CONTENT_LABEL_VALUES_EDUCATION,
)


def _fold_text(text: Any) -> str:
    if text is None:
        return ""
    folded = str(text).lower()
    folded = folded.replace("ç", "c")
    folded = folded.replace("ğ", "g")
    folded = folded.replace("ı", "i")
    folded = folded.replace("ö", "o")
    folded = folded.replace("ş", "s")
    folded = folded.replace("ü", "u")
    folded = re.sub(r"[^a-z0-9]+", " ", folded)
    return re.sub(r"\s+", " ", folded).strip()


def _collect_text_sources(payload: Dict[str, Any]) -> List[str]:
    sources: List[str] = []
    for key in [
        "kitap_adi",
        "baslik",
        "yazar",
        "canonical_summary",
        "kitap_ozeti",
        "book_type",
        "book_subtype",
    ]:
        value = payload.get(key)
        if value:
            sources.append(str(value))
    for section in ["tema_analizi", "kazanim_analizi", "deger_analizi"]:
        for item in payload.get(section, []) or []:
            if isinstance(item, dict):
                name = item.get("ad") or item.get("profil") or ""
                if name:
                    sources.append(str(name))
    return sources


def _extract_signal_hits(text: str, terms: List[str]) -> List[str]:
    folded = _fold_text(text)
    hits = []
    for term in terms:
        if _fold_text(term) in folded:
            hits.append(term)
    return hits


def _score_category(text: str, terms: List[str], bonus_terms: List[str] | None = None) -> Tuple[int, List[str]]:
    folded = _fold_text(text)
    matched = []
    for term in terms:
        if _fold_text(term) in folded:
            matched.append(term)
    bonus = bonus_terms or []
    for term in bonus:
        if _fold_text(term) in folded:
            matched.append(term)
    return len(matched), matched


def build_generic_content_classification(payload: Dict[str, Any]) -> Dict[str, Any]:
    sources = _collect_text_sources(payload)
    combined_text = " \n ".join(sources)
    folded = _fold_text(combined_text)

    category_profiles = {
        "bilim": {
            "terms": [
                "bilim", "bilimsel", "deney", "laboratuvar", "gezegen", "gözlem", "gozlem",
                "araştırma", "arastirma", "teknoloji", "kavram", "keşif", "kesif",
                "bilgi", "scientific"
            ],
            "bonus_terms": ["icad", "gözlemci", "gozlemci", "yorum", "analiz"],
        },
        "biyografi": {
            "terms": [
                "biyografi", "hayati", "yasami", "dogdu", "doğdu", "çocukluğu", "cocuklugu",
                "özgürlük", "ozgurluk", "kişisel", "kisisel", "anilar", "anı", "hayat"
            ],
            "bonus_terms": ["gercek", "gerçek", "yakın", "yakın", "hikaye"],
        },
        "tarih": {
            "terms": [
                "tarih", "tarihsel", "dönem", "donem", "imparatorluk", "sultan", "kral",
                "harita", "mürettebat", "murettebat", "yolculuk", "rota", "sefer", "savaş", "savast", "savas"
            ],
            "bonus_terms": ["yüzyıl", "yuzyil", "devlet", "millet"],
        },
        CONTENT_LABEL_REALISTIC_STORY: {
            "terms": [
                "okul", "aile", "arkadaş", "arkadas", "sokak", "komşu", "komsu",
                "ev", "oda", "sınıf", "sinif", "günlük", "gunluk", "gerçek", "gercek"
            ],
            "bonus_terms": ["duygu", "problem", "sorumluluk"],
        },
        "masal": {
            "terms": [
                "masal", "peri", "prenses", "prens", "kral", "kraliçe", "kraliçe", "sihir", "buyu",
                "büyü", "ejderha", "fantastik", "uyku", "orman"
            ],
            "bonus_terms": ["gizem", "rüya", "ruya"],
        },
        "fabl": {
            "terms": ["fabl", "öğüt", "ogut", "hayvan", "canli", "tavsan", "pati", "ağaç", "agac"],
            "bonus_terms": ["ders", "mesaj", "değer", "deger"],
        },
        CONTENT_LABEL_VALUES_EDUCATION: {
            "terms": [
                "değer", "deger", "sorumluluk", "dayanışma", "dayanisma", "empati",
                "yardımseverlik", "yardimseverlik", "saygı", "saygi", "merhamet", "dostluk"
            ],
            "bonus_terms": ["öğretici", "ogretici", "uyarı", "uyari"]
        },
        "macera": {
            "terms": [
                "macera", "serüven", "seruven", "tehlike", "gizem", "keşif", "kesif",
                "yolculuk", "kurtarma", "kaçış", "kacis", "sır", "sir", "rotası", "rotasi"
            ],
            "bonus_terms": ["karşılaşma", "karsilasma", "yarış", "yaris"]
        },
        "fantastik": {
            "terms": ["fantastik", "sihir", "buyu", "büyü", "ejderha", "peri", "mit", "yaratık"],
            "bonus_terms": ["kutsal", "gizemli", "büyülü", "buyulu"],
        },
    }

    scored = []
    for name, profile in category_profiles.items():
        score, matched = _score_category(combined_text, profile["terms"], profile.get("bonus_terms", []))
        if score:
            scored.append((name, score, matched))

    if not scored:
        return {
            "book_type": {"label": "belirsiz", "confidence": 0.0, "evidence_count": 0, "supporting_signals": []},
            "content": {"label": "belirsiz", "confidence": 0.0, "evidence_count": 0, "supporting_signals": []},
        }

    scored.sort(key=lambda item: (-item[1], item[0]))
    top_label, top_score, top_matches = scored[0]

    book_type_label = top_label
    if top_label == "masal" and any(term in folded for term in ["fabl", "ogut", "öğüt"]):
        book_type_label = "fabl"
    elif top_label == "bilim" and any(term in folded for term in ["tarih", "dönem", "donem", "roman"]):
        book_type_label = "tarih"
    elif top_label == CONTENT_LABEL_VALUES_EDUCATION and any(term in folded for term in ["okul", "aile", "arkadaş", "arkadas"]):
        book_type_label = CONTENT_LABEL_REALISTIC_STORY

    content_label = top_label
    if top_label == "tarih" and any(term in folded for term in ["bilim", "deney", "gözlem", "gozlem"]):
        content_label = "bilim"
    elif top_label == CONTENT_LABEL_REALISTIC_STORY and any(term in folded for term in ["sorumluluk", "dayanisma", "empati", "saygi"]):
        content_label = CONTENT_LABEL_VALUES_EDUCATION

    def _build_classification(label: str, score: int, matches: List[str]) -> Dict[str, Any]:
        confidence = min(0.98, 0.35 + (score / max(1, len(matches) + 2)) * 0.6)
        return {
            "label": label,
            "confidence": round(confidence, 2),
            "evidence_count": max(1, len(matches)),
            "supporting_signals": matches[:8],
        }

    return {
        "book_type": _build_classification(book_type_label, top_score, top_matches),
        "content": _build_classification(content_label, top_score, top_matches),
        "raw_scores": {name: score for name, score, _ in scored[:5]},
    }
