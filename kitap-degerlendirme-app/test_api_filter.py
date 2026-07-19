"""
Test: API'nin false positive filter'i doğru çalıştırıp çalıştırmadığını kontrol et
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test metinleri
test_metinler = {
    "Doğru_Filtre_Test_1": {
        "metin": "Serkan henüz üçüncü sınıfta. Sınıfın en çalışkanı. Derken top havalandı ve yuvarlandı.",
        "beklenen_skor": "0/100",
        "aciklama": "False positive'ler: Serkan (ad), çalışkanı (sıfat), havalandı (fiil), yuvarlandı (fiil)"
    },
    "Gerçek_Risk_Test_2": {
        "metin": "Buraya lan, çık dışarıya! Şeytani ayin yapıyorlarmış.",
        "beklenen_skor": "yüksek (60+)",
        "aciklama": "Gerçek riskler: 'lan' (argo), 'ayin' (okültizm)"
    }
}

print("=" * 80)
print("🧪 API FALSE POSITIVE FILTER TESTİ")
print("=" * 80)

for test_adi, test_data in test_metinler.items():
    print(f"\n📋 TEST: {test_adi}")
    print(f"   Açıklama: {test_data['aciklama']}")
    print(f"   Beklenen: {test_data['beklenen_skor']}")
    print(f"   Metin: {test_data['metin'][:80]}...")
    
    # Dosya oluştur (API, PDF dosyası istediğinden, basit bir PDF simulasyonu yap)
    # Ancak doğrudan evaluator kullanacağız
    from evaluator_maarif import MaarifDegerlendiricisi
    
    evaluator = MaarifDegerlendiricisi()
    sonuc = evaluator.analiz_yap(test_data['metin'], profil='hibrit')
    
    print(f"\n   📊 SONUÇ:")
    print(f"      Risk Skoru: {sonuc['final_skor']}/100")
    print(f"      Karar: {sonuc['karar']['seviye']}")
    print(f"      Bulunan Kategori: {sonuc['kategori_sayisi']}")
    
    # Detaylı bulgular
    for kategori, bulgu_data in sonuc['kategori_bulgulari'].items():
        if bulgu_data['bulundu']:
            print(f"\n      📋 {kategori}: {bulgu_data['toplam_bulgu']} bulgu")
            for i, b in enumerate(bulgu_data['bulunan_kelimeler'][:2], 1):
                print(f"         {i}. '{b['kelime']}' → Risk: {b['baglamsal_risk']}/5")

print("\n" + "=" * 80)
print("✅ TEST TAMAMLANDI")
print("=" * 80)
