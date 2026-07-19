from theme_gain_analysis import _extract_character_profiles, _normalize_main_character_flags


def test_title_only_name_is_not_promoted_without_textual_evidence():
    records = [{"metin": "Kristof Kolomb", "sayfa": 1}]
    characters = _extract_character_profiles(
        records,
        limit=8,
        raw_text="Kristof Kolomb",
        book_title="Benim Adım Kristof Kolomb",
    )

    assert not any((item.get("ad") or item.get("karakter_adi") or "").strip() == "Kristof Kolomb" for item in characters)


def test_title_match_does_not_force_main_character_without_context():
    characters = [{
        "ad": "Kristof Kolomb",
        "karakter_adi": "Kristof Kolomb",
        "entity_type": "PERSON",
        "ana_karakter_puani": 60,
        "guven_skoru": 0.5,
    }]

    normalized = _normalize_main_character_flags(characters, "Benim Adım Kristof Kolomb")

    assert not normalized[0].get("ana_karakter_mi", False)
