from theme_gain_analysis import (
    _empathy_evidence_valid,
    _cross_book_context_audit,
    _teacher_question_specificity_errors,
    analyze_theme_gain,
    classify_entity_type,
    kitap_tutarlilik_denetimi,
    sanitize_character_profiles,
)


assert classify_entity_type("Kyle Keeley") == "PERSON"
assert classify_entity_type("Alexandriaville") == "LOCATION"
assert classify_entity_type("Harika Kubbe") == "OBJECT"
assert classify_entity_type("Bir Tur Bekle") == "GAME_CARD"
assert classify_entity_type("Walter the Farthing Dog") == "BOOK_TITLE"
assert classify_entity_type("Twinky") == "ANIMAL"

characters = sanitize_character_profiles([
    {"ad": "Günaydın Kyle"},
    {"ad": "Üzgünüm Kyle"},
    {"ad": "Birden Kyle"},
    {"ad": "Derken Kyle"},
    {"ad": "Geri Git"},
    {"ad": "Bir Tur Bekle"},
    {"ad": "Kyle Keeley"},
])
names = [item["ad"] for item in characters]
assert names == ["Kyle Keeley"], names
for forbidden in ["Günaydın Kyle", "Üzgünüm Kyle", "Birden Kyle", "Derken Kyle", "Geri Git", "Bir Tur Bekle"]:
    assert forbidden not in names, names
assert all(item.get("entity_type") == "PERSON" for item in characters), characters

assert _empathy_evidence_valid("Kyle ağzının kuruduğunu hissetti.") is False
assert _empathy_evidence_valid("Kyle, Akimi'nin korktuğunu fark etti ve ona destek oldu.") is True

lemoncello_text = """
--- SAYFA 1 ---
Bay Lemoncello kütüphane yarışmasını başlattı ve öğrencilere oyunun kurallarını anlattı.
--- SAYFA 2 ---
Kyle Keeley ve Akimi Hughes ilk bulmacayı çözmek için kitap raflarındaki ipuçlarını araştırdı.
--- SAYFA 3 ---
Miguel Fernandez katalogdaki şifreyi buldu ve bilgiyi Kyle Keeley ile paylaştı.
--- SAYFA 4 ---
Charles Chiltington yarışı kazanmak istedi fakat takım üyeleri adil oyun kuralını savundu.
--- SAYFA 5 ---
Kyle Keeley ve Akimi Hughes birlikte karar vererek kütüphanenin gizli çıkışını aradı.
--- SAYFA 6 ---
Takım, bulmacaları yardımlaşarak çözdü ve kaçış oyununun son ipucuna ulaştı.
"""
result = analyze_theme_gain(
    lemoncello_text,
    {"baslik": "Bay Lemoncello'nun Kütüphanesinden Kaçış", "yazar": "Test"},
    "9-12",
    "standart",
)
assert result["book_type"] == "macera"
assert result["book_subtype"] == "bulmaca / kaçış oyunu"
assert all(item.get("kanit_sayisi", 0) >= 2 for item in result["tema_analizi"]), result["tema_analizi"]
assert all(item.get("bagimsiz_bolum_sayisi", 0) >= 2 for item in result["tema_analizi"]), result["tema_analizi"]

bad_payload = dict(result)
bad_payload["kitap_ozeti"] = result["kitap_ozeti"].replace(
    "kütüphane", "çocukluk mahallesi ve geçmişe özlem", 1
)
bad_audit = kitap_tutarlilik_denetimi(bad_payload)
assert bad_audit["gecerli"] is False, bad_audit
assert bad_audit["cross_book_denetimi"]["gecerli"] is False, bad_audit

generic_questions = ["Takım çalışması neden önemlidir?"]
assert _teacher_question_specificity_errors(result, generic_questions), generic_questions
