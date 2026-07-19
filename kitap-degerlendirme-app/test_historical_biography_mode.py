from theme_gain_analysis import analyze_theme_gain, build_teacher_report_payload


text = """
--- SAYFA 1 ---
Benim adım Kristof Kolomb. Uzak deniz rotalarını merak ettim ve yeni bir rota keşfetmeye karar verdim.
--- SAYFA 2 ---
Kristof Kolomb keşif yapmak için haritayı araştırdı, sefer planı hazırladı ve sarayı ikna etmek için mücadele etti. Saray görevlileri hazırlık sırasında ona destek verdi.
--- SAYFA 3 ---
Kristof Kolomb yeni deniz yolunu keşfetmek için gemileri yönetti. Nina limandan ayrıldı. Pinta yelken açtı. Santa Maria fırtınada ilerledi. Hint Okyanusu haritada gösterildi. Denizciler birbirine destek verdi.
--- SAYFA 4 ---
Dünya haritada görünüyordu. Kanarya rotada kaldı. Karanlık Deniz gemicilerin korktuğu bölge olarak anlatıldı.
--- SAYFA 5 ---
Mürettebat geri dönmek istedi fakat Kristof Kolomb riskleri değerlendirdi ve kararlılıkla devam etme kararı verdi. Arkadaşları zor anda birbirine yardım etti.
--- SAYFA 6 ---
Kristof Kolomb vazgeçmedi, hedefe ulaşmak için azimle mücadele etti, yeni deniz rotasını keşfetti ve keşif günlüğünü yazdı. Denizciler zor işleri yardımlaşarak birlikte tamamladı.
--- SAYFA 7 ---
Denizciler birbirine destek oldu; Kristof Kolomb keşif rotasını yönetti ve yeni deniz yolu için yolculuğu sürdürdü.
"""

result = analyze_theme_gain(text, {"baslik": "Benim Adım Kristof Kolomb", "yazar": "Test"}, "9-12", "standart")
assert result["book_type"] == "tarihî biyografi", result["book_type"]
top_three = [item["ad"] for item in result["tema_analizi"][:3]]
assert top_three[:2] == ["kararlılık", "keşif"], [
    (item["ad"], item.get("tema_gucu"), item.get("farkli_sayfa_sayisi"), item.get("kanit_sayisi"))
    for item in result["tema_analizi"][:6]
]
assert "dayanışma" in top_three, top_three

names = [item["ad"] for item in result["ana_karakterler"]]
for forbidden in ["Kanarya", "Dünya", "Hint Okyanusu", "Pinta", "Nina", "Santa Maria", "Karanlık Deniz"]:
    assert forbidden not in names, (forbidden, names)

teacher = build_teacher_report_payload(result)
courses = " ".join(teacher["kullanilabilecek_dersler"])
for expected in ["Tarih", "Sosyal Bilgiler", "Coğrafya"]:
    assert expected in courses, courses
for leaked in ["mahalle kültürü", "şehirleşme", "komşuluk ilişkileri"]:
    assert leaked not in courses.lower(), courses
