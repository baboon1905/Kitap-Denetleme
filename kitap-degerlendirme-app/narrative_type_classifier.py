from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable


SUPPORTED_NARRATIVE_TYPES = {
    "fiction_story",
    "historical_biography",
    "daily_life_story",
    "animal_responsibility_story",
    "fantasy_story",
    "fairy_tale",
    "memoir",
    "information_book",
    "poem_or_symbolic_text",
    "multiple_story_collection",
}


def fold_text(text: object) -> str:
    folded = unicodedata.normalize("NFKD", str(text or ""))
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    folded = folded.translate(str.maketrans({"ı": "i", "İ": "i", "ş": "s", "Ş": "s"}))
    return folded.lower()


def _count_terms(text: str, terms: Iterable[str]) -> int:
    folded = fold_text(text)
    return sum(1 for term in terms if fold_text(term) in folded)


@dataclass(frozen=True)
class NarrativeTypeResult:
    narrative_type: str
    confidence: float
    signals: dict[str, int | bool | str]


def classify_narrative_type(
    text: str,
    metadata: dict | None = None,
    book_type: str = "",
    book_subtype: str = "",
) -> NarrativeTypeResult:
    metadata = metadata or {}
    title = str(metadata.get("kitap_adi") or metadata.get("baslik") or "")
    combined = f"{title}\n{text or ''}"
    folded = fold_text(combined)
    type_folded = fold_text(f"{book_type} {book_subtype}")

    signals = {
        "historical": _count_terms(combined, [
            "dogdu", "doğdu", "yasami", "yaşamı", "hayati", "hayatı", "biyografi",
            "tarih", "sefer", "kesif", "keşif", "rota", "okyanus", "saray",
            "kral", "kraliçe", "yolculuk", "yılında",
        ]),
        "animal_care": _count_terms(combined, [
            "hayvan", "tavsan", "tavşan", "kedi", "kopek", "köpek", "canli",
            "canlı", "evcil", "sahiplen", "bakim", "bakım", "besle", "veteriner",
            "emanet",
        ]),
        "fantasy": _count_terms(combined, [
            "buyu", "büyü", "sihir", "masal", "peri", "ejderha", "krallik",
            "krallık", "dus", "düş", "karabasan", "gizemli", "parlak tohum",
        ]),
        "fairy_tale": _count_terms(combined, [
            "masal", "bir varmis", "peri", "dev", "prenses", "prens",
            "sihirli", "buyulu", "iyilik", "kotuluk", "tekerleme",
        ]),
        "memoir": _count_terms(combined, [
            "hatirlad", "hatırlad", "anilar", "anılar", "cocuklug", "çocukluğ",
            "yillar sonra", "yıllar sonra", "eski gun", "eski gün", "ozlem", "özlem",
        ]),
        "information": _count_terms(combined, [
            "nedir", "aciklar", "açıklar", "bilgi", "bilim", "deney", "gozlem",
            "gözlem", "kavram", "ornegin", "örneğin", "tanım", "teknoloji",
        ]),
        "collection": _count_terms(combined, [
            "icindekiler", "içindekiler", "oyku 1", "öykü 1", "masal 1",
            "birinci hikaye", "ikinci hikaye", "dizide yer alan kitaplar",
        ]),
        "poem": _count_terms(combined, [
            "siir", "şiir", "dize", "kita", "kıta", "sembol", "imge", "uyak",
        ]),
        "daily": _count_terms(combined, [
            "okul", "sinif", "sınıf", "arkadas", "arkadaş", "aile", "anne",
            "baba", "mahalle", "sokak", "ev", "park", "sorumluluk", "yardim",
        ]),
        "dialogue": len(re.findall(r"['\"]| dedi\b| sordu\b| diye ", folded)),
    }

    if "tarih" in type_folded or "biyografi" in type_folded:
        return NarrativeTypeResult("historical_biography", 0.9, signals)
    if "bilimsel" in type_folded or "bilgilendirici" in type_folded:
        return NarrativeTypeResult("information_book", 0.88, signals)
    if signals["animal_care"] >= 3 and _count_terms(combined, ["sorumluluk", "bak", "sahiplen", "emanet"]) >= 1:
        return NarrativeTypeResult("animal_responsibility_story", 0.88, signals)
    if signals["fairy_tale"] >= 2:
        return NarrativeTypeResult("fairy_tale", 0.86, signals)
    if signals["fantasy"] >= 2 or "fantastik" in type_folded:
        return NarrativeTypeResult("fantasy_story", 0.86, signals)
    if signals["collection"] >= 2:
        return NarrativeTypeResult("multiple_story_collection", 0.74, signals)
    if signals["poem"] >= 2 and signals["daily"] < 2:
        return NarrativeTypeResult("poem_or_symbolic_text", 0.72, signals)
    if signals["information"] >= 2 and signals["dialogue"] < 2:
        return NarrativeTypeResult("information_book", 0.76, signals)
    if signals["memoir"] >= 2:
        return NarrativeTypeResult("memoir", 0.78, signals)
    if signals["daily"] >= 2:
        return NarrativeTypeResult("daily_life_story", 0.74, signals)
    return NarrativeTypeResult("fiction_story", 0.64, signals)


def narrative_type_from_payload(payload: dict) -> str:
    existing = str((payload or {}).get("narrative_type") or "")
    if existing in SUPPORTED_NARRATIVE_TYPES:
        return existing
    return classify_narrative_type(
        str((payload or {}).get("raw_text") or (payload or {}).get("metin") or ""),
        {
            "kitap_adi": (payload or {}).get("kitap_adi"),
            "baslik": (payload or {}).get("baslik"),
        },
        str((payload or {}).get("book_type") or ""),
        str((payload or {}).get("book_subtype") or ""),
    ).narrative_type
