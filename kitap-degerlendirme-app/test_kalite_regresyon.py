#!/usr/bin/env python3
"""Son kalite motoru regresyon testleri."""

from evaluator_maarif import MaarifDegerlendiricisi
from report_generator import RaporOlusturucu
from visual_audit import analyze_extracted_images


def kategori_bulgulari(sonuc, kategori):
    return sonuc["kategori_bulgulari"].get(kategori, {}).get("bulunan_kelimeler", [])


def riskli_var_mi(bulgular):
    return any(float(bulgu.get("riskPuani", bulgu.get("baglamsal_risk", 0)) or 0) > 0 for bulgu in bulgular)


def risk0_savunma_kelimeleri(sonuc):
    rapor = RaporOlusturucu()
    hazir = rapor._tutarlilik_denetime_hazirla(sonuc)
    tum_bulgular = rapor._tum_bulgular(hazir)
    return {
        str(bulgu.get("kelime", "")).lower()
        for bulgu in tum_bulgular
        if rapor._karar_durumu(bulgu) == "risk_0"
    }


def tema_var_mi(sonuc, tema_adi):
    return any(
        bulgu.get("tema_adi") == tema_adi
        for bulgu in sonuc["tema_olay_orgusu_bulgulari"]["bulgular"]
    )


def tema_riski(sonuc, tema_adi):
    return max(
        (
            float(bulgu.get("riskPuani", bulgu.get("risk_puani", 0)) or 0)
            for bulgu in sonuc["tema_olay_orgusu_bulgulari"]["bulgular"]
            if bulgu.get("tema_adi") == tema_adi
        ),
        default=0,
    )


evaluator = MaarifDegerlendiricisi()

sigara = evaluator.analiz_yap("Fosur fosur sigara içer.", profil="hibrit", yas_grubu="10-15")
assert riskli_var_mi(kategori_bulgulari(sigara, "zararlı_alışkanlıklar"))
assert any(b.get("tema_adi") == "Sigara kullanımı" for b in sigara["tema_olay_orgusu_bulgulari"]["bulgular"])
assert tema_riski(sigara, "Sigara kullanımı") >= 4
assert sigara["final_skor"] >= 30

sarhos = evaluator.analiz_yap("Günün yirmi dört saati sarhoştu.", profil="hibrit", yas_grubu="10-15")
assert riskli_var_mi(kategori_bulgulari(sarhos, "zararlı_alışkanlıklar"))
assert any(b.get("tema_adi") == "Sarhoşluk" for b in sarhos["tema_olay_orgusu_bulgulari"]["bulgular"])
assert tema_riski(sarhos, "Sarhoşluk") >= 4
assert sarhos["final_skor"] >= 30

zararli_aliskanlik = evaluator.analiz_yap(
    "Fosur fosur sigara içer. Günün yirmi dört saati sarhoştu. Kavgalı dövüşlü filmleri severdik.",
    profil="hibrit",
    yas_grubu="10-15",
)
assert zararli_aliskanlik["final_skor"] >= 40
assert zararli_aliskanlik["karar"]["seviye"] == "EDİTORYAL İNCELEME GEREKLİ"
assert zararli_aliskanlik["zararli_aliskanlik_skor_kurali"]["minimum_genel_risk"] >= 45
assert zararli_aliskanlik["zararli_aliskanlik_skor_kurali"]["zararli_aliskanlik_carpani"] >= 1.49
assert zararli_aliskanlik["meb_degerlendirmesi"]["meb_kriterler"]["guvenlik"]["risk"] >= 4
assert 70 <= zararli_aliskanlik["meb_degerlendirmesi"]["meb_puani"] <= 85
rapor_riski = RaporOlusturucu()._risk_formulu_bilgisi(zararli_aliskanlik)
assert rapor_riski["toplam"] >= 45
assert RaporOlusturucu()._karar_etiketi(rapor_riski["toplam"]) == "EDİTORYAL İNCELEME GEREKLİ"

gokyuzu_zararli = evaluator.analiz_yap(
    "Fosur fosur sigara içer. Günün yirmi dört saati sarhoştu. "
    "O kadar sarhoş olmasına karşın yine de sokakta rastladıklarına takılır, şakalaşırdı.",
    profil="hibrit",
    yas_grubu="10-15",
)
gokyuzu_kural = gokyuzu_zararli["zararli_aliskanlik_skor_kurali"]
assert 60 <= gokyuzu_zararli["final_skor"] < 70
assert RaporOlusturucu()._karar_etiketi(65) == "EDİTORYAL İNCELEME GEREKLİ"
assert RaporOlusturucu()._karar_etiketi(70) == "YAYINA UYGUN DEĞİLDİR"
assert gokyuzu_kural["tema_yogunlugu_katsayisi_uygulandi"]
assert gokyuzu_kural["tema_tekrar_yogunlugu_var"]
assert gokyuzu_kural["tekrar_eden_temalar"].get("sarhosluk", 0) >= 2
assert not gokyuzu_kural["tekrar_katsayisi_uygulandi"]
assert gokyuzu_kural["davranis_normalizasyonu_var"]
assert gokyuzu_kural["yas_katsayisi_uygulandi"]
assert gokyuzu_kural["minimum_genel_risk"] >= 60
assert 55 <= gokyuzu_zararli["meb_degerlendirmesi"]["meb_puani"] <= 70
assert tema_riski(gokyuzu_zararli, "Sarhoşluk") >= 5

romantik_yogunluk = evaluator.analiz_yap(
    "Küçük âşığım gibi davranırdım. Ondan hoşlanıyordum ve romantik bir çekim hissediyordum.",
    profil="hibrit",
    yas_grubu="10-15",
)
assert tema_var_mi(romantik_yogunluk, "Romantik ilgi")
assert riskli_var_mi(kategori_bulgulari(romantik_yogunluk, "cinsellik_mahremiyet"))

hayranlik_notr = evaluator.analiz_yap(
    "Hayrandım ben ona. Onu örnek alır, yaptıklarını dikkatle izlerdim.",
    profil="hibrit",
    yas_grubu="10-15",
)
assert not tema_var_mi(hayranlik_notr, "Romantik ilgi")

formul_kontrol = RaporOlusturucu()._tutarlilik_denetime_hazirla({
    "final_skor": 40,
    "kategori_bulgulari": {},
    "tema_olay_orgusu_bulgulari": {"bulgular": []},
    "meb_degerlendirmesi": {"meb_puani": 80},
    "metadata": {
        "gorsel_ozet": {
            "toplam_gorsel": 3,
            "gorsel_icerik_analizi_yapildi": False,
        }
    },
})
formul = formul_kontrol["risk_hesaplama_formulu"]
assert formul["gorsel_riski"] == 0
assert formul["gorsel_belirsizlik_riski"] == 25
assert formul["gorsel_belirsizlik_puana_dahil_mi"] is False
assert formul["gorsel_belirsizlik_riski"] > 0
assert formul["gorsel_analiz_yapildi"] is False
assert formul_kontrol["final_skor"] == formul["toplam"]
assert formul["dogrulama_formulu"].endswith(f"= {formul['toplam']:.2f}")
assert formul_kontrol["zorunlu_kalite_kontrolu"]["son_kalite_kontrol_sorulari"]["gorsel_icerik_analizi_eksik_mi"] is True
assert "Görsel içerik analizi eksik yapıldı" in formul_kontrol["zorunlu_kalite_kontrolu"]["eksikler"]
assert "Görsel içerik analizi eksik yapıldı" in formul_kontrol["tutarlilik_denetimi"]["notlar"]
assert formul_kontrol["rapor_durumu"] == "Eksik Analiz"
assert formul_kontrol["zorunlu_kalite_kontrolu"]["rapor_durumu"] == "Eksik Analiz"
assert formul_kontrol["zorunlu_kalite_kontrolu"]["rapor_olusturulabilir"] is False
assert formul_kontrol["zorunlu_kalite_kontrolu"]["son_rapor_dogrulama_cevabi"] == "HAYIR"

gorsel_test = analyze_extracted_images(
    [
        {"sayfa": 2, "gorsel_no": 1, "data": b"temiz", "mime_type": "image/png"},
        {"sayfa": 23, "gorsel_no": 1, "data": b"riskli", "mime_type": "image/png"},
    ],
    provider=lambda image_bytes, meta: {
        "gorsel_aciklamasi": (
            "Elinde sigara bulunan yetişkin karakter"
            if meta["sayfa"] == 23 else
            "Sade kapak ve dekoratif çizim"
        ),
        "genel_guven": 0.88,
        "bulgular": (
            [{
                "kategori": "zararli_aliskanlik",
                "gorsel_aciklamasi": "Elinde sigara bulunan yetişkin karakter",
                "risk_puani": 4,
                "karar_guveni": 0.91,
            }]
            if meta["sayfa"] == 23 else []
        ),
    },
)
assert gorsel_test["gorsel_icerik_analizi_yapildi"] is True
assert len(gorsel_test["gorsel_analizleri"]) == 2
assert any(kayit["risk_puani"] == 0 for kayit in gorsel_test["gorsel_analizleri"])
assert any(kayit["risk_puani"] == 4 for kayit in gorsel_test["gorsel_analizleri"])
assert gorsel_test["zararli_aliskanlik"]["puan"] == 4

meb_detay = zararli_aliskanlik["meb_degerlendirmesi"]["puanlama_detayi"]
assert meb_detay["formul"].startswith("100 - kademeli_toplam_ceza")
assert meb_detay["toplam_ceza"] == sum(
    detay["puan_cezasi"] for detay in meb_detay["kriter_cezalari"].values()
)
assert meb_detay["kriter_cezalari"]["guvenlik"]["puan_cezasi"] < 50
assert "otomatik -50" in meb_detay["kalibrasyon_notu"]

meb_tablo_formul_payload = {
    "final_skor": 70,
    "kategori_bulgulari": {},
    "tema_olay_orgusu_bulgulari": {"bulgular": []},
    "meb_degerlendirmesi": {
        "meb_puani": 59,
        "genel_karar": "Koşullu",
        "meb_kriterler": {
            "guvenlik": {"ad": "Güvenli ve Etik İçerik", "risk": 0, "karar": "Uygun", "puan_cezasi": 0},
        },
        "puanlama_detayi": {
            "baslangic_puani": 100,
            "toplam_ceza": 41,
            "formul": "100 - kademeli_toplam_ceza(41) = 59",
            "kriter_cezalari": {
                "guvenlik": {"risk": 5, "bulgu_sayisi": 3, "puan_cezasi": 41, "karar": "Yüksek Risk"},
            },
        },
    },
}
assert evaluator._meb_tablosu_formulle_tutarsiz_mi(meb_tablo_formul_payload)
hazir_meb_payload = RaporOlusturucu()._tutarlilik_denetime_hazirla(meb_tablo_formul_payload)
assert hazir_meb_payload["meb_degerlendirmesi"]["meb_kriterler"]["guvenlik"]["risk"] == 5
assert hazir_meb_payload["meb_degerlendirmesi"]["meb_kriterler"]["guvenlik"]["puan_cezasi"] == 41
assert RaporOlusturucu()._meb_tablo_cezasi_toplami(hazir_meb_payload) == 41
assert not RaporOlusturucu().consistency_assert(hazir_meb_payload, raise_on_error=False)["hatalar"]
assert RaporOlusturucu()._karar_etiketi(65) == "EDİTORYAL İNCELEME GEREKLİ"

gokyuzu_kural = gokyuzu_zararli["zararli_aliskanlik_skor_kurali"]
assert gokyuzu_kural["tema_yogunlugu_katsayisi_uygulandi"]
assert not gokyuzu_kural["tekrar_katsayisi_uygulandi"]
assert gokyuzu_kural["benzersiz_zararli_tema_sayisi"] >= 2

raporlayici = RaporOlusturucu()
assert raporlayici._pdf_metni_temizle("DÃ¼ÅŸÃ¼k Risk") == "Düşük Risk"
assert raporlayici._pdf_metni_temizle("DÃ¼ÅŸÃ¼k") == "Düşük"
assert raporlayici._pdf_metni_temizle("Uretken") == "Üretken"
assert raporlayici._pdf_metni_temizle("Sorgulayici") == "Sorgulayıcı"
assert raporlayici._pdf_metni_temizle("Iradeli") == "İradeli"

kavga = evaluator.analiz_yap("Kavgalı dövüşlü filmleri severdik.", profil="hibrit", yas_grubu="10-15")
assert not tema_var_mi(kavga, "Kavga")
assert not tema_var_mi(kavga, "Dövüş")
assert not riskli_var_mi(kategori_bulgulari(kavga, "siddet_suc"))
assert "kavgalı" in risk0_savunma_kelimeleri(kavga)

dogrudan_kavga = evaluator.analiz_yap("Çocuklar kavga etti.", profil="hibrit", yas_grubu="10-15")
assert tema_var_mi(dogrudan_kavga, "Kavga")
assert riskli_var_mi(kategori_bulgulari(dogrudan_kavga, "siddet_suc"))

siddet_olumlama = evaluator.analiz_yap("Kavgayı çok sever, dövüşmeyi eğlenceli bulurdu.", profil="hibrit", yas_grubu="10-15")
assert tema_var_mi(siddet_olumlama, "Kavga") or tema_var_mi(siddet_olumlama, "Dövüş")
assert riskli_var_mi(kategori_bulgulari(siddet_olumlama, "siddet_suc"))

negatif_hirsizlik = [
    "Babamın yanında çalıştım.",
    "Çalışıyor musun?",
    "Çalımları komikti.",
    "Çalık kırmızıbiberleri doğramaya çalışıyor.",
]
for metin in negatif_hirsizlik:
    sonuc = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="10-15")
    assert not tema_var_mi(sonuc, "Hırsızlık"), metin
    assert not riskli_var_mi(kategori_bulgulari(sonuc, "siddet_suc")), metin
    assert sonuc["zorunlu_kalite_kontrolu"]["consistency_assert"]["gecti"], metin

pozitif_hirsizlik = [
    "Saati çaldı.",
    "Parayı çalmaya çalıştı.",
    "Cüzdanı çalındı.",
    "Hırsızlık yaptı.",
]
for metin in pozitif_hirsizlik:
    sonuc = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="10-15")
    assert tema_var_mi(sonuc, "Hırsızlık"), metin
    assert riskli_var_mi(kategori_bulgulari(sonuc, "siddet_suc")), metin
    assert sonuc["zorunlu_kalite_kontrolu"]["consistency_assert"]["gecti"], metin

negatif_tema_olay_baglami = [
    ("sigara kelimesi listede yer alıyor", "Sigara kullanımı"),
    ("sigara içmek ifadesi sözlükte açıklanıyor", "Sigara kullanımı"),
    ("alkol ifadesi raporda analiz edildi", "Alkol kullanımı"),
    ("kavga sahnesi ifadesi bir kategori adıdır", "Kavga"),
    ("yumruk atmak terimi analiz kategorisine eklendi", "Şiddet"),
    ("göz göze geldik", "Romantik ilgi"),
    ("kimseyle göz göze gelmedi", "Romantik ilgi"),
    ("yüzü asıktı", "Romantik ilgi"),
    ("ona dayı dememden hoşlanırdı", "Romantik ilgi"),
    ("hoşlanırdı", "Romantik ilgi"),
    ("Onu severdi.", "Romantik ilgi"),
    ("Onu sayardı.", "Romantik ilgi"),
    ("Ona değer verirdi.", "Romantik ilgi"),
    ("Dayı ona gülümsedi.", "Romantik ilgi"),
    ("Amca onu severdi.", "Romantik ilgi"),
    ("Abi ona değer verirdi.", "Romantik ilgi"),
    ("Teyze onu sayardı.", "Romantik ilgi"),
    ("Hala onu severdi.", "Romantik ilgi"),
    ("kendiyle bile dalga geçerdi", "Zorbalık"),
    ("Dalga geçmek ifadesi kullanıldı.", "Zorbalık"),
    ("Kimi zaman dalga geçerdi.", "Zorbalık"),
    ("kardeşim açlıktan bağırıp çağırıyordu", "Aile çatışması"),
    ("gidi erik hırsızları", "Hırsızlık"),
    ("sevgili eşi Kadriye Hanım", "Flört"),
    ("metresini değil milimetresini", "Evlilik dışı ilişki"),
    ("sivil polisleri gördükçe", "Hırsızlık"),
    ("polisler geldi", "Hırsızlık"),
    ("vururlar yüreğimden", "Şiddet eğilimi"),
]
for metin, tema in negatif_tema_olay_baglami:
    sonuc = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="10-15")
    assert not tema_var_mi(sonuc, tema), f"{metin} -> {tema}"
    assert sonuc["zorunlu_kalite_kontrolu"]["consistency_assert"]["gecti"], metin

hitap_memnuniyeti = evaluator.analiz_yap(
    "Ona dayı dememden hoşlanırdı.",
    profil="hibrit",
    yas_grubu="10-15",
)
assert not tema_var_mi(hitap_memnuniyeti, "Romantik ilgi")
assert not tema_var_mi(hitap_memnuniyeti, "Flört")
assert not tema_var_mi(hitap_memnuniyeti, "Mahrem yakınlaşma")
assert not riskli_var_mi(kategori_bulgulari(hitap_memnuniyeti, "cinsellik_mahremiyet"))
assert hitap_memnuniyeti["zorunlu_kalite_kontrolu"]["consistency_assert"]["gecti"]

mecazi_romantik = evaluator.analiz_yap(
    "Filmlerdeki çaresiz âşık bendim.",
    profil="hibrit",
    yas_grubu="10-15",
)
assert not tema_var_mi(mecazi_romantik, "Romantik ilgi")
assert not riskli_var_mi(kategori_bulgulari(mecazi_romantik, "cinsellik_mahremiyet"))

ilk_asik_tema = evaluator.analiz_yap(
    "Ben de senin ilk âşıklarından biriyim.",
    profil="hibrit",
    yas_grubu="10-15",
)
assert not tema_var_mi(ilk_asik_tema, "Romantik ilgi")
assert not riskli_var_mi(kategori_bulgulari(ilk_asik_tema, "cinsellik_mahremiyet"))

pozitif_tema_olay_baglami = [
    ("sigara içer", "Sigara kullanımı"),
    ("Çocuk sigara içer", "Sigara kullanımı"),
    ("Adam içki içti", "Alkol kullanımı"),
    ("sarhoştu", "Sarhoşluk"),
    ("cüzdanı çaldı", "Hırsızlık"),
    ("yumruk attı", "Şiddet"),
    ("dudaktan öptü", "Mahrem yakınlaşma"),
    ("Ondan hoşlanıyordu ve romantik bir çekim hissediyordu.", "Romantik ilgi"),
    ("Arkadaşıyla dalga geçip onu küçük düşürdü.", "Zorbalık"),
]
for metin, tema in pozitif_tema_olay_baglami:
    sonuc = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="10-15")
    assert tema_var_mi(sonuc, tema), f"{metin} -> {tema}"
    assert sonuc["zorunlu_kalite_kontrolu"]["consistency_assert"]["gecti"], metin

gecersiz_tema_sonucu = evaluator.analiz_yap("Temiz bir paragraf.", profil="hibrit", yas_grubu="10-15")
gecersiz_tema_sonucu["tema_olay_orgusu_bulgulari"]["bulgular"].append({
    "tema_adi": "Romantik ilgi",
    "kategori": "cinsellik_mahremiyet",
    "sayfa": 1,
    "cumle": "göz göze geldik",
})
assert not evaluator.consistency_assert(gecersiz_tema_sonucu, raise_on_error=False)["gecti"]

pdf_kapi_sonucu = {
    "kategori_bulgulari": {
        "cinsellik_mahremiyet": {
            "bulunan_kelimeler": [{
                "tema_adi": "Romantik ilgi",
                "kategori": "cinsellik_mahremiyet",
                "sayfa": 1,
                "riskPuani": 1,
                "kararSinifi": "dusuk_risk",
            }],
            "toplam_bulgu": 1,
            "riskli_bulgu_sayisi": 0,
            "dusuk_risk_sayisi": 1,
            "temizlenen_bulgu_sayisi": 0,
        }
    },
    "tema_olay_orgusu_bulgulari": {
        "bulgular": [{
            "tema_adi": "Romantik ilgi",
            "kategori": "cinsellik_mahremiyet",
            "sayfa": 1,
            "cumle": "göz göze geldik",
            "riskPuani": 1,
            "kanitPuani": 0.35,
        }]
    },
}
assert not RaporOlusturucu().consistency_assert(pdf_kapi_sonucu, raise_on_error=False)["gecti"]

eski_payload = {
    "final_skor": 17.73,
    "kategori_bulgulari": {
        "cinsellik_mahremiyet": {
            "bulunan_kelimeler": [{
                "tema_adi": "Romantik ilgi",
                "kategori": "cinsellik_mahremiyet",
                "sayfa": 1,
                "cumle": "göz göze geldik",
                "riskPuani": 1,
                "kaynak": "Tema ve olay örgüsü analizi",
                "baglamTipi": "tema_olay_orgusu",
            }],
            "toplam_bulgu": 1,
            "riskli_bulgu_sayisi": 0,
            "dusuk_risk_sayisi": 1,
            "temizlenen_bulgu_sayisi": 0,
        },
        "siddet_suc": {
            "bulunan_kelimeler": [{
                "tema_adi": "Hırsızlık",
                "kategori": "siddet_suc",
                "sayfa": 1,
                "cumle": "gidi erik hırsızları!",
                "riskPuani": 3,
                "kaynak": "Tema ve olay örgüsü analizi",
                "baglamTipi": "tema_olay_orgusu",
            }],
            "toplam_bulgu": 1,
            "riskli_bulgu_sayisi": 1,
            "dusuk_risk_sayisi": 0,
            "temizlenen_bulgu_sayisi": 0,
        },
    },
    "tema_olay_orgusu_bulgulari": {
        "bulgular": [
            {"tema_adi": "Romantik ilgi", "kategori": "cinsellik_mahremiyet", "sayfa": 1, "cumle": "göz göze geldik", "riskPuani": 1},
            {"tema_adi": "Hırsızlık", "kategori": "siddet_suc", "sayfa": 1, "cumle": "gidi erik hırsızları!", "riskPuani": 3},
        ]
    },
}
temiz_payload = evaluator.tema_bulgularini_kanit_kontroluyle_temizle(eski_payload)
assert temiz_payload["tema_olay_orgusu_bulgulari"]["toplam_bulgu"] == 0
assert temiz_payload["final_skor"] == 0.0
assert not kategori_bulgulari(temiz_payload, "cinsellik_mahremiyet")
assert not kategori_bulgulari(temiz_payload, "siddet_suc")

for sonuc in (sigara, sarhos, kavga):
    kalite = sonuc["zorunlu_kalite_kontrolu"]
    assert kalite["tema_kontrolu"]["kategoriye_tasinmayan_tema_sayisi"] == 0
    sorular = kalite["son_kalite_kontrol_sorulari"]
    assert "riskli_alinti_eksik_mi" in sorular
    assert "puanlama_formulu_sonuc_tutarsiz_mi" in sorular
    assert "kategori_tema_eslesmesi_hatali_mi" in sorular

bozuk_payload = evaluator.analiz_yap("DÃ¼ÅŸÃ¼k riskli metin.", profil="hibrit", yas_grubu="10-15")
assert bozuk_payload["zorunlu_kalite_kontrolu"]["son_kalite_kontrol_sorulari"]["utf8_karakter_bozulmasi_var_mi"]
assert bozuk_payload["zorunlu_kalite_kontrolu"]["rapor_olusturulabilir"] is False

from meb_basit_raporlayici import MEBBulgularıRaporlayıcı
from text_quality import collect_text_quality_issues, looks_mojibake
meb_raporlayici = MEBBulgularıRaporlayıcı()
assert meb_raporlayici._bulgu_alintisi({"alinti": "Sayfa alıntısı"}) == "Sayfa alıntısı"
assert meb_raporlayici._havuzdan_alinti_bul(
    {"sayfa": 31, "kelime": "Sigara kullanımı"},
    "guvenlik",
    meb_raporlayici._alinti_havuzu({
        "tema_olay_orgusu_bulgulari": {
            "bulgular": [{
                "tema_adi": "Sigara kullanımı",
                "kategori": "zararlı_alışkanlıklar",
                "sayfa": 31,
                "alinti": "Fosur fosur sigara içer.",
            }]
        }
    })
) == "Fosur fosur sigara içer."

dogru_turkce_payload = {
    "detayli_rapor": "╔════╗\n║ çaresiz âşık, dükkânlar açıldı, “yakında aç kalacağız” ║",
    "cumle": "68o filmlerdeki çaresiz âşık bendim.",
}
assert not looks_mojibake(dogru_turkce_payload["cumle"])
assert collect_text_quality_issues(dogru_turkce_payload) == []
assert looks_mojibake("DÃ¼ÅŸÃ¼k")

stale_sayac_payload = {
    "final_skor": 0,
    "kategori_bulgulari": {
        "cinsellik_mahremiyet": {
            "bulunan_kelimeler": [{
                "kelime": "Romantik ilgi",
                "kategori": "cinsellik_mahremiyet",
                "cumle": "Ben de senin ilk asiklarindan biriyim.",
                "sayfa": 1,
                "riskPuani": 0,
                "baglamsal_risk": 0,
                "kararSinifi": "baglamla_temiz",
                "baglamTipi": "romantik_dusuk_izleme",
            }],
            "toplam_bulgu": 1,
            "riskli_bulgu_sayisi": 0,
            "dusuk_risk_sayisi": 1,
            "temizlenen_bulgu_sayisi": 0,
        },
        "siddet_suc": {
            "bulunan_kelimeler": [{
                "kelime": "kavgali",
                "kategori": "siddet_suc",
                "cumle": "Biz cocuklar ozellikle kavgali dovuslu filmleri severdik.",
                "sayfa": 42,
                "riskPuani": 0,
                "baglamsal_risk": 0,
                "kararSinifi": "baglamla_temiz",
                "baglamTipi": "siddet_referansi_dusuk",
            }],
            "toplam_bulgu": 1,
            "riskli_bulgu_sayisi": 0,
            "dusuk_risk_sayisi": 1,
            "temizlenen_bulgu_sayisi": 0,
        },
    },
    "tema_olay_orgusu_bulgulari": {"bulgular": []},
}
rapor_kapisi = RaporOlusturucu().consistency_assert(stale_sayac_payload, raise_on_error=False)
assert rapor_kapisi["gecti"]

assert not evaluator._romantik_ilgi_kaniti_var_mi("Filmlerdeki çaresiz aşık bendim.")
assert not evaluator._romantik_ilgi_kaniti_var_mi("Ona hayrandım ve onu örnek alırdım.")
assert not evaluator._romantik_ilgi_kaniti_var_mi("Ben de senin ilk aşıklarından biriyim.")
assert not evaluator._romantik_ilgi_kaniti_var_mi("Ondan hoşlanırdım ama bu eski bir hatıraydı.")
assert evaluator._romantik_ilgi_kaniti_var_mi("Birbirlerinden hoşlanıyorlardı.")
assert evaluator._romantik_ilgi_kaniti_var_mi("İki karakter sevgili olmuş ve el ele geziyordu.")

gorsel_belirsizlik_formulu = RaporOlusturucu()._risk_formulu_bilgisi({
    "final_skor": 0,
    "meb_degerlendirmesi": {"meb_puani": 100},
    "gorsel_tarama": {
        "toplam_gorsel": 3,
        "gorsel_icerik_analizi_yapildi": False,
    },
})
assert gorsel_belirsizlik_formulu["gorsel_riski"] == 0
assert gorsel_belirsizlik_formulu["gorsel_belirsizlik_riski"] == 25
assert gorsel_belirsizlik_formulu["gorsel_belirsizlik_puana_dahil_mi"] is False
assert gorsel_belirsizlik_formulu["gorsel_katkisi"] == 0
assert gorsel_belirsizlik_formulu["toplam"] == 0

mantiksal_kalite_payload = {
    "kategori_bulgulari": {
        "cinsellik_mahremiyet": {
            "bulunan_kelimeler": [{
                "tema_adi": "Romantik ilgi",
                "kelime": "Romantik ilgi",
                "cumle": "Filmlerdeki çaresiz aşık bendim.",
                "riskPuani": 1,
                "baglamsal_risk": 1,
                "kararSinifi": "dusuk_risk",
                "nihaiKarar": "Düşük Risk",
            }]
        }
    }
}
assert evaluator._romantik_yanlis_pozitif_var_mi(mantiksal_kalite_payload)

print("Kalite regresyon testleri geçti.")
