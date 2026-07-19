from theme_gain_analysis import (
    _pedagogical_evaluation,
    analyze_theme_gain,
    build_pdf_report,
    build_teacher_report_payload,
    build_word_report,
    sanitize_character_profiles,
)


sample_text = """
--- SAYFA 1 ---
Benim adım Bülent. Yıllar sonra mahalleye döndüm ve çocukluğumun sokağını yağmur altında hatırladım.
--- SAYFA 2 ---
Bülent eski komşuların sesini düşünürken Çiçek Abla ona çocukluk günlerini hatırlattı. Kıymet Teyze kapının önünde beklerdi.
--- SAYFA 3 ---
Ayhan Işık mahallede herkesin konuştuğu bir isimdi. Emrullah Efendi babamın dükkânının yanından geçerken selam verirdi.
--- SAYFA 4 ---
Sibel Öğretmen okulda çocukları dinler, Tuna Abi ise sokaktaki çocuklara yardım ederdi. Çiçek Abla ve Kıymet Teyze mahallede sık sık anılırdı.
--- SAYFA 5 ---
Bülent bütün bu kişileri hatırladıkça eski mahalle ile yeni şehir arasındaki değişimi daha iyi görür.
--- SAYFA 6 ---
Ayhan Işık yeniden anıldı, Emrullah Efendi çocuklarla konuştu ve Sibel Öğretmen Bülent'i dinledi.
--- SAYFA 7 ---
Tuna Abi sokakta Bülent'e yardım etti; Çiçek Abla ile Kıymet Teyze eski günleri konuştu.
--- SAYFA 8 ---
Sır Çilek kapının yanında bekledi, Saçmalama Çilek dedi Bülent ama Birkaç yalnızca cümlenin başında kaldı.
--- SAYFA 9 ---
Çilek mahallede yeniden göründü ve Bülent ile konuştu. Böyle, Yine, Senin, Yıllar ve Herkes kişi adı değildi.
--- SAYFA 10 ---
Bunu kimse karakter sanmamalı; Bana Sürekli İçeri diye başlayan söz de kişi ilişkisi kurmamalı.
--- SAYFA 11 ---
Annem, Bülent hemen eve gelir misin yavrum diye seslendi; Bülent anlatıcı adayı olarak güçlendi.
--- SAYFA 12 ---
Sibel Öğretmen yoklama aldı. Sibel Öğretmen defteri açtı. Sibel Öğretmen sınıfta bekledi.
--- SAYFA 13 ---
Sibel Öğretmen çocukları dinledi. Sibel Öğretmen okulda yeniden göründü.
"""


result = analyze_theme_gain(sample_text, {"baslik": "Karakter Testi", "yazar": "Test"}, "9-12", "standart")
characters = result["ana_karakterler"]
names = [item["ad"] for item in characters]
categories = {item["ad"]: item.get("kategori") for item in characters}

assert "Bülent" in names
assert categories["Bülent"] == "anlatıcı"
bülent = next(item for item in characters if item["ad"] == "Bülent")
sibel = next(item for item in characters if item["ad"] == "Sibel Öğretmen")
assert bülent.get("anlatici_mi") is True, bülent
assert bülent.get("ana_karakter_mi") is True, characters
assert bülent.get("ana_karakter_puani", 0) > sibel.get("ana_karakter_puani", 0), (bülent, sibel)
assert not sibel.get("ana_karakter_mi"), sibel

for full_name in ["Ayhan Işık", "Emrullah Efendi", "Sibel Öğretmen", "Çiçek Abla", "Kıymet Teyze", "Tuna Abi", "Çilek"]:
    assert full_name in names, names

for fragment in ["Işık", "Kıymet"]:
    assert fragment not in names, names

for fake_name in ["Sır Çilek", "Saçmalama Çilek", "Birkaç", "Başka", "Böyle", "Yine", "Senin", "Yıllar", "Herkes", "Bunu", "Bana", "Sürekli", "İçeri"]:
    assert fake_name not in names, names

assert all(item.get("guven_skoru") is not None for item in characters)
assert any(item.get("ana_karakter_mi") for item in characters)
assert any(item.get("kategori") == "yan karakter" for item in characters)

for character in characters:
    assert character.get("karakter_adi"), character
    assert character.get("rolu") in {"ana", "yan"}, character
    assert character.get("metindeki_gorunme_sayisi", 0) >= 2 or character.get("kategori") == "anlatıcı", character
    assert character.get("gectigi_sayfa_sayisi", 0) >= 1, character
    assert character.get("karakter_ozeti"), character
    assert character.get("karakter_iliskileri"), character
    assert character.get("eylem_baglam_skoru", 0) >= 1 or character.get("kategori") == "anlatıcı", character
    relation_text = character.get("karakter_iliskileri", "")
    for fake_relation in ["Birkaç", "Başka", "Böyle", "Yine", "Senin", "Yıllar", "Herkes", "Bunu", "Bana", "Sürekli", "İçeri"]:
        assert fake_relation not in relation_text, character
    if " ile aynı olay" in relation_text and "metinde " in relation_text:
        relation_names = relation_text.split("metinde ", 1)[1].split(" ile aynı olay", 1)[0]
        for relation_name in [part.strip() for part in relation_names.split(",") if part.strip()]:
            assert relation_name in names, (relation_name, names, character)


gokyuzu_text = """
--- SAYFA 1 ---
Benim adım Bülent. Yıllar sonra çocukluğumun geçtiği sokağa döndüm ve yağmur altında eski mahalleyi hatırlıyorum.
--- SAYFA 2 ---
Annem, Bülent hemen eve gelir misin yavrum diye seslenirdi. O sesi duyunca çocukluğumun kapıları açıldı.
--- SAYFA 3 ---
Bülent sokakta yürürken babasının dükkânını, annesini ve kardeşi Suna'yı düşündü.
--- SAYFA 4 ---
Çiçek Abla mahallede anılırdı. Çiçek çocukların yanından geçti. Çiçek kapının önünde bekledi.
--- SAYFA 5 ---
Çiçek eski evlerin arasında göründü. Çiçek sokakta konuştu. Çiçek mahallede yeniden anıldı. Çiçek kapıyı açtı. Çiçek çocuklara baktı.
--- SAYFA 6 ---
Çiçek evlerin arasında yürüdü. Çiçek komşularla konuştu. Çiçek sokakta tekrar göründü. Çiçek pencereden baktı.
--- SAYFA 7 ---
Ben o günlerde Dilek'i, Çilek'i, Tuna Abi'yi ve Sibel Öğretmen'i de hatırlıyorum.
--- SAYFA 8 ---
Bülent değişen şehir karşısında eski sokakların kaybolduğunu fark ettim diye düşündü.
--- SAYFA 9 ---
Sonunda Bülent çocukluk anılarının yeni şehirde nasıl eksildiğini gördüm diyerek geçmişe baktı.
"""

gokyuzu_result = analyze_theme_gain(gokyuzu_text, {"baslik": "Gökyüzünü Kaybeden Şehir", "yazar": "Test"}, "9-12", "standart")
gokyuzu_characters = gokyuzu_result["ana_karakterler"]
gokyuzu_by_name = {item["ad"]: item for item in gokyuzu_characters}

assert "Bülent" in gokyuzu_by_name, gokyuzu_characters
assert "Çiçek" in gokyuzu_by_name or "Çiçek Abla" in gokyuzu_by_name, gokyuzu_characters

gokyuzu_bulent = gokyuzu_by_name["Bülent"]
gokyuzu_cicek = gokyuzu_by_name.get("Çiçek") or gokyuzu_by_name.get("Çiçek Abla")

assert gokyuzu_bulent.get("anlatici_mi") is True, gokyuzu_bulent
assert gokyuzu_bulent.get("ana_karakter_mi") is True, gokyuzu_characters
assert gokyuzu_bulent.get("birinci_sahis_anlatim") is True, gokyuzu_bulent
assert gokyuzu_result.get("anlatim_turu") == "birinci_sahis", gokyuzu_result
assert gokyuzu_result.get("anlatici_adi") == "Bülent", gokyuzu_result
assert gokyuzu_result.get("anlatici_tespit_uyarisi") != "Birinci şahıs anlatım bulundu fakat anlatıcı tespit edilemedi", gokyuzu_result
assert gokyuzu_bulent.get("ana_karakter_puani", 0) > gokyuzu_cicek.get("ana_karakter_puani", 0), (gokyuzu_bulent, gokyuzu_cicek)
assert not gokyuzu_cicek.get("ana_karakter_mi"), gokyuzu_cicek
assert gokyuzu_cicek.get("kategori") == "yan karakter", gokyuzu_cicek


emlakci_text = """
--- SAYFA 1 ---
Benim adım Bülent. Çocukluğumun geçtiği mahallemiz yıllar sonra çok değişmişti.
--- SAYFA 2 ---
Bizim Emlakçı Mehmet sokakta çocuklarla konuştu ve eski evlerin satıldığını anlattı.
--- SAYFA 3 ---
Emlakçı Mehmet babamın dükkânının önünde Bülent'e selam verdi.
--- SAYFA 4 ---
Emlakçı Mehmet mahallede yeniden göründü; Çiçek Abla da komşularla konuştu.
--- SAYFA 5 ---
Bülent sokağımızı, annesini ve babasını hatırladım diyerek geçmişe baktı.
"""

emlakci_result = analyze_theme_gain(emlakci_text, {"baslik": "Emlakçı Testi", "yazar": "Test"}, "9-12", "standart")
emlakci_characters = emlakci_result["ana_karakterler"]
emlakci_names = [item["ad"] for item in emlakci_characters]

assert "Bizim Emlakçı Mehmet" not in emlakci_names, emlakci_names
assert emlakci_names.count("Emlakçı Mehmet") == 1, emlakci_names
assert any(item.get("guven_skoru") != 0.98 for item in emlakci_characters), emlakci_characters

word_html = build_word_report(emlakci_result).getvalue().decode("utf-8")
assert "Ana Karakterler" not in word_html
assert "Karakterler ve Anlatıcı Bilgisi" in word_html

pdf_bytes = build_pdf_report(emlakci_result).getvalue()
assert b"Ana Karakterler" not in pdf_bytes


historical_biography_text = """
--- SAYFA 1 ---
Bölüm I Aradığım Hindistan
Kristof Kolomb saraya gitti ve keşif yolculuğu planını kraliçeye anlattı. Kristof Kolomb bilinmeyeni merak ettiği için haritanın başında rotayı yeniden çizdi.
--- SAYFA 2 ---
Portekiz yeni deniz yollarını araştırdı. Portekiz bu kararı yıllar sonra yeniden değerlendirdi.
Hint Okyanusu gemicilerin önünde uzandı. Hint Okyanusu fırtınalarla denizcileri zorladı.
Kanarya ufukta göründü. Kanarya denizcilerin rotasında kaldı. Dünya haritada yuvarlak görünüyordu. Dünya denizcilerin önünde genişledi. Okyanusun ötesi bilinmiyordu. Okyanusun dalgaları gemileri zorladı.
--- SAYFA 3 ---
Nina limandan ayrıldı ve batıya ilerledi. Nina gece boyunca dalgalarla mücadele etti.
Pinta yelkenlerini açtı ve filoya yetişti. Pinta ertesi gün rotasını değiştirdi.
Santa Maria limandan ayrıldı. Santa Maria fırtınada yelkenlerini korudu. Karanlık Deniz ufukta uzandı. Karanlık Deniz gemicileri korkuttu.
--- SAYFA 4 ---
Büyük Kanarya kıyıdan uzaklaştı. Büyük Kanarya açık denizde diğer gemileri izledi.
Barcelona limanında tören yapıldı. İspanyol denizciler rotayı inceledi. Katolik Krallar sefer haberini dinledi.
--- SAYFA 5 ---
Kristof Kolomb mürettebatla konuştu ve gemilerin yoluna devam etmesine karar verdi.
Kristof Kolomb keşif günlüğüne okyanusta yaşananları yazdı ve denizcilere seslendi. Kararlılıkla hedefine ulaşmak için mücadele etti, vazgeçmedi ve yolculuğa devam etti.
--- SAYFA 6 ---
Kristof Kolomb yeni bir rota keşfetme kararını savundu. Mürettebat geri dönmek isterken o riskleri değerlendirdi ve seferi sürdürdü.
--- SAYFA 7 ---
Kristof Kolomb bilinmeyen denizleri araştırdı. Merakı ve azmi, karşılaştığı engellere rağmen hedefinden vazgeçmemesini sağladı.
"""

historical_result = analyze_theme_gain(
    historical_biography_text,
    {"baslik": "Benim Adım Kristof Kolomb", "yazar": "Test"},
    "9-12",
    "standart",
)
historical_names = [item["ad"] for item in historical_result["ana_karakterler"]]
assert "Kristof Kolomb" in historical_names, historical_result["ana_karakterler"]
for non_person_name in [
    "Aradığım Hindistan", "Hindistan", "Hint Okyanusu", "Büyük Kanarya", "Portekiz",
    "Nina", "Pinta", "Santa Maria", "Dünya", "Kanarya", "Karanlık Deniz",
    "Barcelona", "İspanyol", "Katolik", "Katolik Krallar", "Okyanusun",
]:
    assert non_person_name not in historical_names, (non_person_name, historical_names)
assert historical_result.get("book_type") == "tarihî biyografi", historical_result.get("book_type")
historical_top_three = [item.get("ad") for item in historical_result.get("tema_analizi", [])[:3]]
assert any(theme in historical_top_three for theme in ["keşif", "merak", "kararlılık"]), historical_top_three
assert historical_result.get("ana_tema") != "dayanışma", historical_top_three
historical_summary = historical_result.get("kitap_ozeti", "")
assert "kaybolan defter" not in historical_summary.lower(), historical_summary
assert "okul ve çevresinde" not in historical_summary.lower(), historical_summary
for historical_context in ["deniz rotası", "gemiler", "mürettebat", "okyanus", "keşif"]:
    assert historical_context in historical_summary.lower(), (historical_context, historical_summary)

teacher_payload = build_teacher_report_payload(historical_result)
pedagogical_text = " ".join(
    teacher_payload.get("kullanilabilecek_dersler", [])
    + teacher_payload.get("kitaba_ozel_etkinlikler", [])
    + teacher_payload.get("tartisma_sorulari", [])
    + _pedagogical_evaluation(historical_result)
).lower()
for leaked_template_phrase in ["mahalle kültürü", "şehirleşme", "komşuluk ilişkileri"]:
    assert leaked_template_phrase not in pedagogical_text, (leaked_template_phrase, pedagogical_text)
assert teacher_payload.get("book_type") == "tarihî biyografi", teacher_payload
assert any("Tarih:" in item for item in teacher_payload.get("kullanilabilecek_dersler", [])), teacher_payload

stale_profiles = sanitize_character_profiles([
    {"ad": "Kristof Kolomb", "karakter_ozeti": "Denizci Kristof Kolomb mürettebatla konuştu."},
    {"ad": "Portekiz", "karakter_ozeti": "Portekiz ülkesi keşif seferlerini destekledi."},
    {"ad": "Hint Okyanusu", "karakter_ozeti": "Coğrafi bölge ve okyanus adıdır."},
    {"ad": "Nina", "karakter_ozeti": "Kristof Kolomb'un keşif yolculuğundaki gemisi ve yelkenlisidir."},
    {"ad": "Pinta", "karakter_ozeti": "Mürettebat taşıyan tarihî gemidir."},
    {"ad": "Dünya", "karakter_ozeti": "Kristof Kolomb'un keşif rotasında geçen coğrafi varlıktır."},
    {"ad": "Kanarya", "karakter_ozeti": "Kristof Kolomb'un deniz yolculuğundaki ada ve coğrafi bölgedir."},
    {"ad": "Karanlık Deniz", "karakter_ozeti": "Kristof Kolomb anlatısındaki deniz ve coğrafi bölgedir."},
])
stale_names = [item["ad"] for item in stale_profiles]
assert stale_names == ["Kristof Kolomb"], stale_profiles
