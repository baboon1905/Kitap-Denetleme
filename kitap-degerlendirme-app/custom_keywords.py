from __future__ import annotations

import copy
import json
import os
import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, Iterable, List

from config import SAKINCALI_KELIMELER


CUSTOM_KEYWORDS_PATH = os.path.abspath("custom_keywords.json")
SYSTEM_OVERRIDES_KEY = "_system_overrides"

CATEGORY_ALIASES = {
    "siddet_ve_suc": "siddet_suc",
    "siddet_suc": "siddet_suc",
    "cinsellik_ve_mahremiyet": "cinsellik_mahremiyet",
    "cinsellik_mahremiyet": "cinsellik_mahremiyet",
    "zararli_aliskanliklar": "zararlı_alışkanlıklar",
    "zararlı_alışkanlıklar": "zararlı_alışkanlıklar",
    "kaba_dil_ve_hakaret": "kaba_dil_hakaret",
    "kaba_dil_hakaret": "kaba_dil_hakaret",
    "ayrimcilik_ve_nefret": "ayrımcılık_nefret",
    "ayrımcılık_nefret": "ayrımcılık_nefret",
    "korku_ve_travma": "korku_travma",
    "korku_travma": "korku_travma",
    "okultizm_ve_batil": "okültizm_batıl",
    "okültizm_batıl": "okültizm_batıl",
    "dijital_risk": "dijital_risk",
    "olumsuz_davranis": "olumsuz_davranış",
    "olumsuz_davranış": "olumsuz_davranış",
    "reklam_ticari": "reklam_ticari",
}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _slug(value: str) -> str:
    value = str(value or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("ı", "i")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_category(category: str) -> str:
    raw = str(category or "").strip()
    if raw in SAKINCALI_KELIMELER:
        return raw
    return CATEGORY_ALIASES.get(_slug(raw), raw)


def display_categories() -> List[dict]:
    return [
        {
            "key": key,
            "label": data.get("kategori_adi", key.replace("_", " ").title()),
            "alias": next((alias for alias, target in CATEGORY_ALIASES.items() if target == key and alias != key), key),
        }
        for key, data in SAKINCALI_KELIMELER.items()
    ]


def _entry_value(entry: Any) -> str:
    if isinstance(entry, dict):
        return str(entry.get("value") or entry.get("kelime") or entry.get("terim") or "").strip()
    return str(entry or "").strip()


def _entry_active(entry: Any) -> bool:
    return bool(entry.get("active", True)) if isinstance(entry, dict) else True


def _normalize_entries(values: Iterable[Any]) -> List[dict]:
    seen = set()
    cleaned = []
    for raw in values or []:
        value = _entry_value(raw)
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        if isinstance(raw, dict):
            cleaned.append({
                "value": value,
                "active": bool(raw.get("active", True)),
                "updated_at": str(raw.get("updated_at") or raw.get("son_guncelleme") or _now()),
            })
        else:
            cleaned.append({"value": value, "active": True, "updated_at": _now()})
    return cleaned


def _active_values(values: Iterable[Any]) -> List[str]:
    result = []
    for entry in values or []:
        value = _entry_value(entry)
        if value and _entry_active(entry):
            result.append(value)
    return result


def load_custom_keywords(path: str = CUSTOM_KEYWORDS_PATH) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            raw = json.load(file)
    except Exception:
        return {}
    return normalize_custom_keywords(raw)


def normalize_custom_keywords(raw: Any) -> Dict[str, dict]:
    normalized: Dict[str, dict] = {SYSTEM_OVERRIDES_KEY: {}}
    if not isinstance(raw, dict):
        return normalized

    overrides = raw.get(SYSTEM_OVERRIDES_KEY, {})
    if isinstance(overrides, dict):
        for category, terms in overrides.items():
            target_category = normalize_category(category)
            if target_category not in SAKINCALI_KELIMELER or not isinstance(terms, dict):
                continue
            normalized[SYSTEM_OVERRIDES_KEY].setdefault(target_category, {})
            for term, meta in terms.items():
                if not str(term).strip():
                    continue
                meta = meta if isinstance(meta, dict) else {}
                normalized[SYSTEM_OVERRIDES_KEY][target_category][str(term).strip()] = {
                    "active": bool(meta.get("active", True)),
                    "updated_at": str(meta.get("updated_at") or _now()),
                }

    for category, value in raw.items():
        if category == SYSTEM_OVERRIDES_KEY:
            continue
        target_category = normalize_category(category)
        if target_category not in SAKINCALI_KELIMELER:
            continue
        if isinstance(value, list):
            keywords = value
            regexes = []
        elif isinstance(value, dict):
            keywords = value.get("keywords", value.get("kelimeler", []))
            regexes = value.get("regex", value.get("regexler", []))
        else:
            keywords = []
            regexes = []
        normalized[target_category] = {
            "keywords": _normalize_entries(keywords),
            "regex": _normalize_entries(regexes),
        }
    return normalized


def save_custom_keywords(data: Dict[str, dict], path: str = CUSTOM_KEYWORDS_PATH) -> Dict[str, dict]:
    normalized = normalize_custom_keywords(data)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(normalized, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return normalized


def _system_override(data: Dict[str, dict], category: str, term: str) -> dict:
    return (data.get(SYSTEM_OVERRIDES_KEY, {}).get(category, {}) or {}).get(term, {})


def set_system_term_active(category: str, term: str, active: bool, data: Dict[str, dict] | None = None) -> Dict[str, dict]:
    data = data if data is not None else load_custom_keywords()
    category = normalize_category(category)
    data.setdefault(SYSTEM_OVERRIDES_KEY, {}).setdefault(category, {})[term] = {
        "active": bool(active),
        "updated_at": _now(),
    }
    return save_custom_keywords(data)


def add_or_update_custom_term(
    category: str,
    term: str,
    term_type: str = "keywords",
    active: bool = True,
    old_category: str | None = None,
    old_term: str | None = None,
    old_type: str | None = None,
    data: Dict[str, dict] | None = None,
) -> Dict[str, dict]:
    data = data if data is not None else load_custom_keywords()
    category = normalize_category(category)
    term_type = "regex" if term_type == "regex" else "keywords"
    term = str(term or "").strip()
    if not term:
        return save_custom_keywords(data)

    if old_term:
        remove_custom_term(old_category or category, old_term, old_type or term_type, data=data, persist=False)

    bucket = data.setdefault(category, {"keywords": [], "regex": []})
    bucket.setdefault("keywords", [])
    bucket.setdefault("regex", [])
    entries = [entry for entry in bucket[term_type] if _entry_value(entry).casefold() != term.casefold()]
    entries.append({"value": term, "active": bool(active), "updated_at": _now()})
    bucket[term_type] = entries
    return save_custom_keywords(data)


def remove_custom_term(
    category: str,
    term: str,
    term_type: str = "keywords",
    data: Dict[str, dict] | None = None,
    persist: bool = True,
) -> Dict[str, dict]:
    data = data if data is not None else load_custom_keywords()
    category = normalize_category(category)
    term_type = "regex" if term_type == "regex" else "keywords"
    bucket = data.get(category, {})
    bucket[term_type] = [
        entry for entry in bucket.get(term_type, [])
        if _entry_value(entry).casefold() != str(term or "").strip().casefold()
    ]
    return save_custom_keywords(data) if persist else data


def list_keyword_records(data: Dict[str, dict] | None = None) -> List[dict]:
    data = data if data is not None else load_custom_keywords()
    records = []
    for category, base in SAKINCALI_KELIMELER.items():
        label = base.get("kategori_adi", category)
        risk = base.get("risk_puani", 0)
        context_rule = base.get("bağlam_notu") or base.get("baglam_notu") or "Varsayılan bağlam analizi"
        for term in base.get("kelimeler", []):
            override = _system_override(data, category, term)
            records.append({
                "id": f"system::{category}::{term}",
                "term": term,
                "kategori": category,
                "kategori_adi": label,
                "risk_turu": "Kelime / ifade",
                "risk_puani": risk,
                "baglam_kurali": context_rule,
                "active": bool(override.get("active", True)),
                "kaynak": "Sistem",
                "updated_at": override.get("updated_at", "Sistem varsayılanı"),
                "editable": False,
            })

    for category, bucket in data.items():
        if category == SYSTEM_OVERRIDES_KEY or category not in SAKINCALI_KELIMELER:
            continue
        base = SAKINCALI_KELIMELER[category]
        for term_type, risk_type in (("keywords", "Kelime / ifade"), ("regex", "Regex")):
            for entry in bucket.get(term_type, []):
                records.append({
                    "id": f"custom::{category}::{term_type}::{_entry_value(entry)}",
                    "term": _entry_value(entry),
                    "kategori": category,
                    "kategori_adi": base.get("kategori_adi", category),
                    "risk_turu": risk_type,
                    "tip": term_type,
                    "risk_puani": base.get("risk_puani", 0),
                    "baglam_kurali": base.get("bağlam_notu") or base.get("baglam_notu") or "Varsayılan bağlam analizi",
                    "active": _entry_active(entry),
                    "kaynak": "Özel",
                    "updated_at": entry.get("updated_at", ""),
                    "editable": True,
                })
    return records


def validate_custom_keywords(data: Dict[str, dict] | None = None) -> dict:
    data = data if data is not None else load_custom_keywords()
    records = [record for record in list_keyword_records(data) if record.get("active")]
    owners: Dict[str, List[dict]] = {}
    invalid_regex = []

    for record in records:
        owners.setdefault(record["term"].casefold(), []).append(record)
        if record.get("kaynak") == "Özel" and record.get("tip") == "regex":
            try:
                re.compile(record["term"])
            except re.error as exc:
                invalid_regex.append({"kategori": record["kategori"], "regex": record["term"], "hata": str(exc)})

    duplicates = [
        {
            "kelime": term,
            "kategoriler": sorted({item["kategori"] for item in items}),
            "kaynaklar": sorted({item["kaynak"] for item in items}),
        }
        for term, items in owners.items()
        if len(items) > 1
    ]
    system_custom_duplicates = [
        item for item in duplicates
        if "Sistem" in item["kaynaklar"] and "Özel" in item["kaynaklar"]
    ]
    cross_category_duplicates = [
        item for item in duplicates
        if len(item["kategoriler"]) > 1
    ]

    warnings = []
    if system_custom_duplicates:
        warnings.append("Aynı kelime hem sistem hem özel listede tanımlanmış.")
    if cross_category_duplicates:
        warnings.append("Aynı kelime iki farklı kategoriye atanmış.")
    if invalid_regex:
        warnings.append("Geçersiz özel regex tanımı var.")
    return {
        "duplicates": duplicates,
        "system_custom_duplicates": system_custom_duplicates,
        "cross_category_duplicates": cross_category_duplicates,
        "invalid_regex": invalid_regex,
        "warnings": warnings,
        "ok": not warnings,
    }


def custom_keyword_summary(data: Dict[str, dict] | None = None) -> dict:
    data = data if data is not None else load_custom_keywords()
    categories = []
    for category, bucket in data.items():
        if category == SYSTEM_OVERRIDES_KEY or category not in SAKINCALI_KELIMELER:
            continue
        base = SAKINCALI_KELIMELER.get(category, {})
        keyword_count = len([entry for entry in bucket.get("keywords", []) if _entry_active(entry)])
        regex_count = len([entry for entry in bucket.get("regex", []) if _entry_active(entry)])
        categories.append({
            "kategori": category,
            "kategori_adi": base.get("kategori_adi", category.replace("_", " ").title()),
            "keyword_count": keyword_count,
            "regex_count": regex_count,
            "total_count": keyword_count + regex_count,
        })
    return {
        "categories": sorted(categories, key=lambda item: item["kategori_adi"]),
        "total_keywords": sum(item["keyword_count"] for item in categories),
        "total_regex": sum(item["regex_count"] for item in categories),
        "validation": validate_custom_keywords(data),
    }


def get_merged_risk_dictionary() -> Dict[str, dict]:
    merged = copy.deepcopy(SAKINCALI_KELIMELER)
    custom = load_custom_keywords()
    for category, base in merged.items():
        base["kelimeler"] = [
            term for term in base.get("kelimeler", [])
            if bool(_system_override(custom, category, term).get("active", True))
        ]
        base["regexler"] = []

    for category, bucket in custom.items():
        if category == SYSTEM_OVERRIDES_KEY or category not in merged:
            continue
        merged[category].setdefault("kelimeler", [])
        merged[category].setdefault("regexler", [])
        merged[category]["kelimeler"] = list(dict.fromkeys(
            list(merged[category].get("kelimeler", [])) + _active_values(bucket.get("keywords", []))
        ))
        merged[category]["regexler"] = list(dict.fromkeys(
            list(merged[category].get("regexler", [])) + _active_values(bucket.get("regex", []))
        ))
    return merged
