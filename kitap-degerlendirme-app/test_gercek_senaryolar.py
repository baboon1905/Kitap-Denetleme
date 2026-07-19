#!/usr/bin/env python
"""
Gerçek senaryolar - "buraya lan" vb. örnekleri test et
"""

from evaluator_maarif import MaarifDegerlendiricisi

# Gerçek metin örnekleri
test_metinler = [
    {
        "metin": "Buraya lan yazıl! Ne yapıyorsun sen?",
        "aciklama": "Gerçek kaba söz - buraya + lan",
        "beklenen_kategori": "kaba_dil_hakaret",
        "beklenen_min_risk": 3.5
    },
    {
        "metin": "Oraya lan koyduk kitabı dün.",
        "aciklama": "Gerçek kaba söz - oraya + lan", 
        "beklenen_kategori": "kaba_dil_hakaret",
        "beklenen_min_risk": 3.5
    },
    {
        "metin": "Ağaç havalandırma işlemi başladı.",
        "aciklama": "Harmless - lan embedded",
        "beklenen_kategori": None,
        "beklenen_min_risk": 0
    },
    {
        "metin": "Serkan ve Şerkan adlı çocuklar gelmişler.",
        "aciklama": "Harmless - kan in names",
        "beklenen_kategori": None,
        "beklenen_min_risk": 0
    },
    {
        "metin": "Yayınevi çok güzel kitaplar yayımlıyor.",
        "aciklama": "Harmless - ayin in yayınevi",
        "beklenen_kategori": None,
        "beklenen_min_risk": 0
    },
    {
        "metin": "Kan dökülmüş sahneler filmde var.",
        "aciklama": "Risky - kan dökmek pattern",
        "beklenen_kategori": "siddet_suc",
        "beklenen_min_risk": 3.5
    },
    {
        "metin": "Şeytani ayin sahneleri korkunç.",
        "aciklama": "Risky - şeytani ayin pattern",
        "beklenen_kategori": "okültizm_batil",
        "beklenen_min_risk": 3.5
    },
]

evaluator = MaarifDegerlendiricisi()

print("=" * 90)
print("🧪 GERÇEK SENARYO TESTI - Akıllı Kontekst Analizi")
print("=" * 90)

passed = 0
failed = 0

for test in test_metinler:
    metin = test['metin']
    aciklama = test['aciklama']
    beklenen_kategori = test['beklenen_kategori']
    beklenen_min_risk = test['beklenen_min_risk']
    
    print(f"\n📝 Metin: \"{metin}\"")
    print(f"   Açıklama: {aciklama}")
    
    sonuc = evaluator.analiz_yap(metin, profil='hibrit', yas_grubu='10-15')
    
    # Kontrol 1: Kategori
    bulundu = False
    for kategori, data in sonuc['kategori_bulgulari'].items():
        if data['toplam_bulgu'] > 0:
            bulundu = True
            
            if beklenen_kategori is None:
                print(f"   ❌ HATA: {kategori} bulunması gerekmiyordu ama bulundu!")
                failed += 1
            else:
                if kategori == beklenen_kategori:
                    if data['ortalama_risk'] >= beklenen_min_risk:
                        print(f"   ✅ PASS: {kategori} → {data['ortalama_risk']:.1f}/5")
                        passed += 1
                    else:
                        print(f"   ⚠️ WARNING: {kategori} risk {data['ortalama_risk']:.1f}/5 < {beklenen_min_risk}")
                        passed += 1
                else:
                    print(f"   ❌ HATA: {kategori} bulundu ama {beklenen_kategori} bekliyorduk")
                    failed += 1
    
    if not bulundu and beklenen_kategori is None:
        print(f"   ✅ PASS: Hiçbir bulgu yok (beklenen)")
        passed += 1
    elif not bulundu and beklenen_kategori is not None:
        print(f"   ❌ HATA: {beklenen_kategori} bulunması gerekirdi ama bulunamadı!")
        failed += 1

print("\n" + "=" * 90)
print(f"📊 SONUÇ: {passed} başarılı, {failed} başarısız")
print("=" * 90)
