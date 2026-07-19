from theme_gain_analysis import _report_scores, prepare_theme_report_payload, rapor_kalite_kapisi


base = {
    "kitap_adi": "Benim Adım Kristof Kolomb",
    "book_type": "tarihî biyografi",
    "ana_tema": "kararlılık",
    "tema_analizi": [{"ad": "kararlılık", "tema_gucu": 92, "kanitlar": []}],
    "ilk_uc_baskin_tema": [{"ad": "kararlılık", "tema_gucu": 92, "kanitlar": []}],
    "ana_karakterler": [
        {"ad": "Kristof Kolomb", "rolu": "yan", "ana_karakter_mi": False, "ana_karakter_puani": 80},
        {"ad": "Filipa Monis", "rolu": "yan", "ana_karakter_puani": 30},
        {"ad": "Filipa Moniz", "rolu": "yan", "ana_karakter_puani": 28},
    ],
}

prepared = prepare_theme_report_payload(base)
characters = prepared["ana_karakterler"]
assert len([item for item in characters if item["ad"].startswith("Filipa Moni")]) == 1, characters
kristof = next(item for item in characters if item["ad"] == "Kristof Kolomb")
assert kristof["ana_karakter_mi"] is True and kristof["rolu"] == "ana", kristof
assert prepared["karakter_kalite_degerlendirmesi"]["skor"] < 90, prepared["karakter_kalite_degerlendirmesi"]
assert _report_scores(prepared)["Karakter Derinliği"] < 90, _report_scores(prepared)

invalid = dict(base)
invalid["ana_karakterler"] = list(base["ana_karakterler"]) + [
    {"ad": "Hint Okyanusu", "rolu": "yan", "karakter_ozeti": "Coğrafi bölge ve okyanus adıdır."}
]
gate = rapor_kalite_kapisi(invalid)
assert gate["durum"] == "FAIL", gate
assert any("kişi olmayan" in error for error in gate["hatalar"]), gate
