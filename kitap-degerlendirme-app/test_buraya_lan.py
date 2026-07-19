#!/usr/bin/env python
"""
"buraya lan" testleri - yeni smart context analysis
"""

from evaluator_maarif import MaarifDegerlendiricisi

test_cases = [
    ("Buraya lan! Ne yapıyorsun?", "RİSK YÜKSEK", "buraya lan = kaba söz"),
    ("Ağaç havalandı ve havası açıldı", "RİSK DÜŞÜK", "lan embedded = zararsız"),
    ("Ya lan! Ulan ne var?", "RİSK YÜKSEK", "ya lan, ulan = hakaret"),
    ("Oraya lan yazacak mıydı?", "RİSK YÜKSEK", "oraya lan = kaba söz"),
    ("Şuraya lan koyduk dün", "RİSK YÜKSEK", "şuraya lan = kaba söz"),
    ("Serkan geldi okula", "RİSK DÜŞÜK", "Serkan = isim"),
    ("Çalışkan bir kız", "RİSK DÜŞÜK", "çalışkan = sıfat"),
    ("Kan dökülmüş yerde", "RİSK YÜKSEK", "kan dökmek = şiddet"),
]

evaluator = MaarifDegerlendiricisi()

print("=" * 80)
print("🧪 SMART CONTEXT ANALYSIS TEST")
print("=" * 80)

for metin, beklenen, açıklama in test_cases:
    print(f"\n📝 Metin: \"{metin}\"")
    print(f"   Açıklama: {açıklama}")
    print(f"   Beklenen: {beklenen}")
    
    sonuc = evaluator.analiz_yap(metin, profil='hibrit', yas_grubu='10-15')
    
    # Problematik kategoriyi bul
    for kategori, data in sonuc['kategori_bulgulari'].items():
        if data['toplam_bulgu'] > 0:
            print(f"\n   ✅ Kategori: {kategori}")
            print(f"      Bulgu Sayısı: {data['toplam_bulgu']}")
            print(f"      Ort. Risk: {data['ortalama_risk']:.1f}/5")
            
            for i, bulgu in enumerate(data['bulunan_kelimeler'][:2], 1):
                kelime = bulgu['kelime']
                risk = bulgu['baglamsal_risk']
                print(f"      {i}. \"{kelime}\" → Risk: {risk}/5")

print("\n" + "=" * 80)
print("✅ TEST TAMAMLANDI")
print("=" * 80)
