from theme_gain_analysis import (
    _summary_has_forbidden_content,
    analyze_theme_gain,
    character_quality_assessment,
    kitap_tutarlilik_denetimi,
    sanitize_character_profiles,
)


text = """
--- SAYFA 1 ---
Bay Lemoncello yeni kütüphanenin açılışı için öğrencilere bir yarışma ve oyun hazırladı.
--- SAYFA 2 ---
Öğrenciler kütüphanede kilitli kaldı ve çıkış yolunu bulmak için ilk bulmacayı çözmeye karar verdi.
--- SAYFA 3 ---
Takım üyeleri kitap raflarındaki ipuçlarını birlikte araştırdı ve buldukları bilgileri paylaştı.
--- SAYFA 4 ---
Bir grup katalogdaki şifreyi çözerken diğer öğrenciler gizli kodu inceleyerek yeni bir ipucu buldu.
--- SAYFA 5 ---
Yarışmayı kazanmak isteyen öğrenciler kurallara uymak ile rakiplerini geçmek arasında karar verdi.
--- SAYFA 6 ---
Takım çalışması sayesinde bulmacalar çözüldü; öğrenciler yardımlaşarak kütüphanenin çıkışına yaklaştı.
--- SAYFA 7 ---
Oyun, adil rekabetin ve bilgiyi paylaşmanın yalnız hareket etmekten daha etkili olduğunu gösterdi.
"""

result = analyze_theme_gain(
    text,
    {"baslik": "Bay Lemoncello'nun Kütüphanesinden Kaçış", "yazar": "Test"},
    "9-12",
    "standart",
)
assert result["book_type"] == "macera", result["book_type"]
top_themes = [item["ad"] for item in result["tema_analizi"][:5]]
assert "problem çözme" in top_themes, top_themes
assert any(theme in top_themes for theme in ["takım çalışması", "adil rekabet", "okuma kültürü"]), top_themes
summary = result["kitap_ozeti"].lower()
for stale_phrase in ["çocukluğunun geçtiği", "kaybolan defter", "eski mahalle hayatı"]:
    assert stale_phrase not in summary, summary
audit = kitap_tutarlilik_denetimi(result)
assert audit["gecerli"] is True, audit
assert _summary_has_forbidden_content("Öğrenciler zaman baskısı altında bulmacaları çözer.") is False

ocr_characters = sanitize_character_profiles([
    {"ad": "Kutu"},
    {"ad": "Bay Lemon"},
    {"ad": "Cello"},
    {"ad": "Kütüphanesinden Kaçış"},
    {"ad": "Kyle Keeley"},
])
assert [item["ad"] for item in ocr_characters] == ["Bay Lemoncello", "Kyle Keeley"], ocr_characters
character_audit = character_quality_assessment({
    "kitap_adi": "Bay Lemoncello'nun Kütüphanesinden Kaçış",
    "book_type": "macera",
    "ana_karakterler": ocr_characters,
})
assert character_audit["gecerli"] is True, character_audit
