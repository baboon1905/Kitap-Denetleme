from evaluator_maarif import MaarifDegerlendiricisi


def kategori_bulgulari(sonuc, kategori):
    return sonuc["kategori_bulgulari"].get(kategori, {}).get("bulunan_kelimeler", [])


def riskli_var_mi(bulgular):
    return any(float(bulgu.get("riskPuani", bulgu.get("baglamsal_risk", 0)) or 0) > 0 for bulgu in bulgular)


evaluator = MaarifDegerlendiricisi()

metin = (
    "Adam fosur fosur sigara içiyordu. "
    "Sonra meyhaneden çıktı ve sarhoştu. "
    "İki çocuk kavga etti. "
    "Ayşe sevgilisinden hoşlanıyordu ve el ele tuttular. "
    "İki karakter öpüştüler."
)

sonuc = evaluator.analiz_yap(metin, profil="hibrit", yas_grubu="6-12")
kalite = sonuc["zorunlu_kalite_kontrolu"]

assert kalite["uygulandi"] is True
assert kalite["rapor_olusturulabilir"] is True
assert kalite["son_rapor_dogrulama_cevabi"] == "EVET"

tespit_edilen = set(kalite["tema_kontrolu"]["tespit_edilen_zorunlu_temalar"])
beklenen_temalar = {"Sigara kullanımı", "Alkol kullanımı", "Sarhoşluk", "Kavga", "Romantik ilgi", "Flört", "Öpüşme"}
assert beklenen_temalar <= tespit_edilen, f"Eksik temalar: {sorted(beklenen_temalar - tespit_edilen)}"

assert riskli_var_mi(kategori_bulgulari(sonuc, "zararlı_alışkanlıklar"))
assert riskli_var_mi(kategori_bulgulari(sonuc, "cinsellik_mahremiyet"))
assert riskli_var_mi(kategori_bulgulari(sonuc, "siddet_suc"))

print("Zorunlu kalite kontrolü testi geçti.")
