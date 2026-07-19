from theme_gain_analysis import sanitize_character_profiles


profiles = sanitize_character_profiles([
    {
        "ad": "Filipa Monis",
        "metindeki_gorunme_sayisi": 3,
        "gectigi_sayfa_sayisi": 2,
        "guven_skoru": 0.71,
    },
    {
        "ad": "Filipa Moniz",
        "metindeki_gorunme_sayisi": 4,
        "gectigi_sayfa_sayisi": 3,
        "guven_skoru": 0.76,
    },
    {"ad": "Kristof Kolomb", "metindeki_gorunme_sayisi": 8, "guven_skoru": 0.9},
    {"ad": "Kral Fernando", "metindeki_gorunme_sayisi": 2, "guven_skoru": 0.7},
    {"ad": "Sayar Fernando", "metindeki_gorunme_sayisi": 3, "guven_skoru": 0.72},
])

filipa = [item for item in profiles if item["ad"].startswith("Filipa Moni")]
assert len(filipa) == 1, profiles
assert filipa[0]["metindeki_gorunme_sayisi"] == 7, filipa[0]
assert {"Filipa Monis", "Filipa Moniz"} & set(filipa[0].get("normalized_aliases", [])), filipa[0]
fernando = [item for item in profiles if item["ad"] == "Kral Fernando"]
assert len(fernando) == 1, profiles
assert fernando[0]["metindeki_gorunme_sayisi"] == 5, fernando[0]
assert "Sayar Fernando" in fernando[0].get("normalized_aliases", []), fernando[0]
assert len(profiles) == 3, profiles
