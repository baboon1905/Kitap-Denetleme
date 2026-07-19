"""
TEST: Gerçek metinle False Positive Filter Kontrolü
"""

from evaluator_maarif import MaarifDegerlendiricisi

test_metinler = [
    {
        "ad": "Test 1: Havalandı (false positive)",
        "metin": "Derken top havalandı. Serkan oradaydi. Çızlık sesı koptu."
    },
    {
        "ad": "Test 2: Yuvarlandı (false positive)",
        "metin": "Top yuvarlandı piste. Çalışkan çocuklar oynuyordu."
    },
    {
        "ad": "Test 3: Gerçek risk - buraya lan",
        "metin": "Buraya lan dedi adam. Kendi işine bak."
    },
    {
        "ad": "Test 4: Yayınevi (false positive)",
        "metin": "Yayınevi kitapları basıyor. Serkan romanını yazmış."
    },
]

evaluator = MaarifDegerlendiricisi()

for test in test_metinler:
    print(f"\n{'='*70}")
    print(f"📌 {test['ad']}")
    print(f"📝 Metin: {test['metin']}")
    print(f"{'='*70}")
    
    sonuc = evaluator.analiz_yap(test['metin'], profil='hibrit')
    
    print(f"\n📊 Final Skor: {sonuc['final_skor']}/100")
    print(f"🎯 Karar: {sonuc['karar']['seviye']}")
    
    # Detaylı bulgular
    toplam_bulgu = sum(sonuc['kategori_bulgulari'][k]['toplam_bulgu'] 
                      for k in sonuc['kategori_bulgulari'])
    
    if toplam_bulgu > 0:
        print(f"\n🔍 Toplam Bulgu: {toplam_bulgu}")
        for kategori, bulgu_data in sonuc['kategori_bulgulari'].items():
            if bulgu_data['bulundu']:
                print(f"\n   📋 {kategori}:")
                for bulgu in bulgu_data['bulunan_kelimeler']:
                    print(f"      • '{bulgu['kelime']}' → Risk: {bulgu['baglamsal_risk']}/5")
    else:
        print(f"✅ Hiç bulgular yok (temiz metin)")

print(f"\n{'='*70}")
print("✅ TEST TAMAMLANDI")
print(f"{'='*70}")
