from theme_gain_analysis import analyze_theme_gain, build_word_report, prepare_theme_report_payload, _fold_text


text = """
--- SAYFA 1 ---
Benim adım Bülent. Hadi Kıymet diye başlayan bir cümle vardı ama bu bir karakter adı değildi. Şimdi herkes sokakta toplandı.
--- SAYFA 2 ---
Oysa Gülfem sözü cümlenin başında geçti; gerçek karakter adı gibi alınmamalı. Bülent, Çiçek Abla ve Kıymet Teyze ile konuştu.
--- SAYFA 3 ---
Ayhan Işık mahallede anılırdı. Emrullah Efendi babanın dükkânı önünde çocuklara selam verdi. Sibel Öğretmen okulda çocukları dinledi.
--- SAYFA 4 ---
Arkadaş kelimesi yalnızca sınıftaki bir kişiyi anlatmak için geçti; paylaşma, güven veya destek olayı anlatılmadı.
--- SAYFA 5 ---
Çevre kelimesi sadece evin çevresi anlamında kullanıldı. Doğa, ağaç, hayvan veya temizlik davranışı anlatılmadı.
--- SAYFA 6 ---
Bir çocuk yolda yardım istedi ama mahalle birlikte hareket etmedi; dayanışma veya imece gibi ortak bir davranış kurulmadı.
--- SAYFA 7 ---
Vatan kelimesi bir tabelada yazıyordu. Bayrak kelimesi de duvarda görüldü ama kimse koruma, görev veya sorumluluk davranışı göstermedi.
--- SAYFA 8 ---
Adalet sözcüğü kitap adında geçti. Güzel kelimesi de bir eşyanın rengini anlatmak için kullanıldı; sanat veya estetik üretim yoktu.
--- SAYFA 9 ---
Geldi ve Koştu cümlenin başında duran fiillerdi. Hemen ve Sonra da yalnızca zarf olarak kullanıldı.
--- SAYFA 10 ---
Öyle konuştu. Fırına gittiler. Sesin uzaktan geldi. Gülümseyerek içeri girdi.
--- SAYFA 11 ---
Yanımda Çiçek yürürken Çiçek Abla çocuklarla konuştu. Yapma Bülent dedi annesi.
--- SAYFA 12 ---
Bülent hemen eve gelir misin yavrum diye seslenildi. Ayhan Işık yeniden anıldı.
--- SAYFA 13 ---
Emrullah Efendi çocuklarla konuştu. Sibel Öğretmen Bülent'i dinledi. Kıymet Teyze ve Çiçek Abla mahallede bekledi.
"""


result = analyze_theme_gain(text, {"baslik": "Filtre Testi", "yazar": "Test"}, "9-12", "standart")
names = [item["ad"] for item in result["ana_karakterler"]]

assert "Bülent" in names
assert "Çiçek Abla" in names
assert "Kıymet Teyze" in names
assert "Ayhan Işık" in names
assert "Emrullah Efendi" in names
assert "Sibel Öğretmen" in names

for fake_name in ["Hadi Kıymet", "Şimdi", "Oysa Gülfem", "Işık", "Kıymet"]:
    assert fake_name not in names, names
for fake_name in ["Geldi", "Koştu", "Hemen", "Sonra"]:
    assert fake_name not in names, names
for fake_name in ["Öyle", "Fırına", "Sesin", "Gülümseyerek", "Yanımda Çiçek", "Yapma Bülent", "Yanımda", "Yapma"]:
    assert fake_name not in names, names
for forbidden_name in ["Bizim", "Şu", "Bu", "O", "Bir", "Birkaç", "Başka", "Herkes", "Kimse", "Senin", "Benim", "Bizimki"]:
    assert forbidden_name not in names, names

for character in result["ana_karakterler"]:
    assert character.get("karakter_adi"), character
    assert character.get("rolu") in {"ana", "yan"}, character
    assert character.get("metindeki_gorunme_sayisi", 0) >= 2 or character.get("kategori") == "anlatıcı", character
    assert character.get("eylem_baglam_skoru", 0) >= 1 or character.get("kategori") == "anlatıcı", character
    assert character.get("karakter_ozeti"), character
    assert character.get("karakter_iliskileri"), character

themes = {item["ad"] for item in result["tema_analizi"]}
values = {item["ad"] for item in result["deger_analizi"]}
profiles = {item.get("ad") or item.get("profil") for item in result["maarif_profili_eslesmeleri"]}

assert "çevre bilinci" not in themes
assert "dostluk" not in themes
assert "dayanışma" not in themes
assert "dayanışma" not in values
assert "yardımseverlik" not in values

for abstract_profile in ["vatansever", "adil", "estetik"]:
    assert abstract_profile not in profiles


spine_text = """
--- SAYFA 1 ---
Anlatıcı yıllar sonra çocukluğunun geçtiği sokağa döndü ve eski günleri hatırladı.
--- SAYFA 2 ---
Yağmur altında yürürken geçmiş mahalle hayatına duyduğu özlem daha da belirginleşti.
--- SAYFA 3 ---
Annesi, babası ve kardeşi Suna ile yaşadığı hatıralar sokaktaki evleri yeniden canlandırdı.
--- SAYFA 4 ---
Eski komşuların ve mahalle esnafının anıları, anlatıcının geçmişe özlem duygusunu güçlendirdi.
--- SAYFA 5 ---
Yeni şehir görüntüsü karşısında eski mahalle düzeninin değiştiğini fark etti.
--- SAYFA 6 ---
Çocukluk anılarını düşündükçe kaybolan sokaklara ve eski günlere duyduğu özlem kitabın ana duygusuna dönüştü.
"""

spine_result = analyze_theme_gain(spine_text, {"baslik": "Omurga Tema", "yazar": "Test"}, "9-12", "standart")
spine_themes = spine_result["tema_analizi"]
assert spine_themes, spine_result
assert spine_themes[0]["ad"] == "geçmişe özlem", spine_themes
assert spine_themes[0].get("yayilim_bonusu", 0) > 0, spine_themes[0]


environment_false_text = """
--- SAYFA 1 ---
Çocuk çevresine baktı ve odadaki insanları gördü.
--- SAYFA 2 ---
Arkadaş çevresi okulda genişti ama doğa, ağaç, fidan veya koruma davranışı anlatılmadı.
--- SAYFA 3 ---
Sosyal çevre içinde herkes birbirini tanırdı; çevre kirliliği ya da doğal yaşamdan söz edilmedi.
"""

environment_result = analyze_theme_gain(environment_false_text, {"baslik": "Çevre Bağlam Testi", "yazar": "Test"}, "9-12", "standart")
environment_themes = {item["ad"] for item in environment_result["tema_analizi"]}
environment_values = {item["ad"] for item in environment_result["deger_analizi"]}

assert "çevre bilinci" not in environment_themes, environment_result["tema_analizi"]
assert "çevre duyarlılığı" not in environment_values, environment_result["deger_analizi"]


environment_true_text = """
--- SAYFA 1 ---
Çocuklar parkta çevre kirliliğini fark etti ve doğayı korumak için çöpleri topladı.
--- SAYFA 2 ---
Sınıf, fidan dikerek yeşil alanı koruma davranışı gösterdi.
"""

environment_true_result = analyze_theme_gain(environment_true_text, {"baslik": "Çevre Doğru Bağlam Testi", "yazar": "Test"}, "9-12", "standart")
environment_true_values = {item["ad"] for item in environment_true_result["deger_analizi"]}
assert "çevre duyarlılığı" in environment_true_values, environment_true_result["deger_analizi"]


metadata_text = """
--- SAYFA 1 ---
Yazar biyografisi: Yazar dostluk, aile, sorumluluk ve dürüstlük konularında kitaplar yazmıştır.
--- SAYFA 2 ---
ISBN 978-605-123-456-7 Baskı bilgisi, yayıncı bilgisi, künye ve telif metinleri bu sayfada yer alır.
--- SAYFA 3 ---
Künye: Okuduğunu anlama, karakter analizi yapma ve değerleri fark etme ifadeleri yalnızca tanıtım bilgisidir.
"""

metadata_result = analyze_theme_gain(metadata_text, {"baslik": "Meta Filtre Testi", "yazar": "Test"}, "9-12", "standart")
for group_name in ["tema_analizi", "deger_analizi", "kazanim_analizi", "maarif_profili_eslesmeleri"]:
    for item in metadata_result.get(group_name, []):
        for evidence in item.get("kanitlar", []):
            folded_quote = _fold_text(evidence.get("alinti", ""))
            assert "isbn" not in folded_quote, (group_name, item)
            assert "kunye" not in folded_quote, (group_name, item)
            assert "biyografi" not in folded_quote, (group_name, item)
            assert "yayinci" not in folded_quote, (group_name, item)


abstract_value_text = """
--- SAYFA 1 ---
Dürüstlük kelimesi sınıf panosunda yazıyordu.
--- SAYFA 2 ---
Dürüst olmak gerektiği tabelada belirtilmişti.
--- SAYFA 3 ---
Doğru davranış kavramı kitaptaki bir başlıkta geçti.
--- SAYFA 4 ---
Gerçek sözcüğü bir liste içinde yer aldı.
--- SAYFA 5 ---
Dürüstlük hakkında genel bir açıklama vardı ama karakter davranışı anlatılmadı.
--- SAYFA 6 ---
Yalan söylemedi ifadesi örnek cümle olarak yazılmıştı; olay sahnesi kurulmadı.
"""

abstract_value_result = analyze_theme_gain(abstract_value_text, {"baslik": "Soyut Değer Testi", "yazar": "Test"}, "9-12", "standart")
for item in abstract_value_result.get("deger_analizi", []):
    if _fold_text(item.get("ad", "")) == "durustluk":
        assert item.get("tema_gucu", 0) <= 79, item
        assert item.get("guclu_davranis_kaniti_sayisi", 0) < 2, item


weak_payload = {
    "kitap_adi": "Zayif Eslesme Testi",
    "yazar": "Test",
    "kitap_ozeti": "Ozet guvenilir uretilemedi.",
    "tema_analizi": [
        {
            "ad": "guclu tema",
            "tur": "tema",
            "tema_gucu": 72,
            "guven_skoru": 0.72,
            "kanit_sayisi": 3,
            "farkli_sayfa_sayisi": 2,
            "baglam_gucu": 3,
            "kanitlar": [
                {
                    "sayfa": 2,
                    "alinti": "Cocuk mahallede yasadigi olayi dusundu ve ailesiyle konustu.",
                    "anahtarlar": ["aile"],
                    "baglam_gucu": 3,
                    "kanit_turu": "olay_sahnesi",
                }
            ],
        }
    ],
    "kazanim_analizi": [
        {
            "ad": "dusuk kazanim",
            "tur": "kazanim",
            "tema_gucu": 35,
            "guven_skoru": 0.35,
            "kanit_sayisi": 1,
            "farkli_sayfa_sayisi": 1,
            "baglam_gucu": 1,
            "kanitlar": [
                {
                    "sayfa": 3,
                    "alinti": "Metin kisa bir ifade verir.",
                    "baglam_gucu": 1,
                    "kanit_turu": "anlati_icerigi",
                }
            ],
        }
    ],
    "deger_analizi": [
        {
            "ad": "kanitsiz deger",
            "tur": "deger",
            "tema_gucu": 65,
            "guven_skoru": 0.65,
            "kanit_sayisi": 0,
            "kanitlar": [],
        }
    ],
    "maarif_profili_eslesmeleri": [],
    "temel_mesajlar": ["şehirye gider ve ve eve doner"],
}

prepared_weak = prepare_theme_report_payload(weak_payload)
weak_names = {item.get("ad") for item in prepared_weak.get("zayif_eslesmeler", [])}

assert "dusuk kazanim" in weak_names, prepared_weak
assert "kanitsiz deger" in weak_names, prepared_weak
assert not prepared_weak.get("kazanim_analizi"), prepared_weak.get("kazanim_analizi")
assert not prepared_weak.get("deger_analizi"), prepared_weak.get("deger_analizi")
assert "şehirye" not in str(prepared_weak), prepared_weak
assert "ve ve" not in str(prepared_weak), prepared_weak

word_html = build_word_report(weak_payload).getvalue().decode("utf-8")
assert "Zayıf Eşleşmeler" in word_html, word_html
assert "dusuk kazanim" in word_html, word_html
assert "şehirye" not in word_html, word_html
assert "ve ve" not in word_html, word_html
