#!/usr/bin/env python
"""
Smart Context Analysis Testi
"lan", "kan", "ayin" gibi problemli kelimelerin doğru filtrelenip filtrelenmediğini test et
"""

from evaluator_maarif import MaarifDegerlendiricisi

print("=" * 80)
print("🔬 SMART CONTEXT ANALYSIS TESTI")
print("=" * 80)

test_cases = [
    {
        "isim": "LAN - Zararsız Bağlam",
        "metin": "Ağaç havalandı ve yaprakları sallandı. Ev de havalandı.",
        "beklenen_risk": "⬇️ DÜŞÜK",
        "kategori": "Kaba Dil"
    },
    {
        "isim": "LAN - Zararlı Bağlam",
        "metin": "Ya lan! Ulan bu ne biçim davranış! Ha lan yine başladı.",
        "beklenen_risk": "⬆️ YÜKSEK",
        "kategori": "Kaba Dil"
    },
    {
        "isim": "KAN - Zararsız Bağlam (İsim)",
        "metin": "Serkan ve çalışkan bir kız tanıştı. Onlar iyi insanlar.",
        "beklenen_risk": "⬇️ DÜŞÜK/SIFIR",
        "kategori": "Şiddet"
    },
    {
        "isim": "KAN - Zararlı Bağlam",
        "metin": "Savaşta çok kan dökülmüştü. Yerde kan akıyor, kanı içinde yatıyor.",
        "beklenen_risk": "⬆️ YÜKSEK",
        "kategori": "Şiddet"
    },
    {
        "isim": "AYIN - Zararsız Bağlam (Yayın)",
        "metin": "Kitap yayınevi tarafından basılmıştır. Yayın tarihi 2020.",
        "beklenen_risk": "⬇️ DÜŞÜK/SIFIR",
        "kategori": "Okültizm"
    },
    {
        "isim": "AYIN - Zararlı Bağlam",
        "metin": "Gece yapılan şeytani ayin sırasında gizli güç çağırıldı. Kanlı ayin ritüeli.",
        "beklenen_risk": "⬆️ YÜKSEK",
        "kategori": "Okültizm"
    }
]

evaluator = MaarifDegerlendiricisi()

for test in test_cases:
    print(f"\n📝 {test['isim']}")
    print(f"   Metin: \"{test['metin'][:50]}...\"")
    print(f"   Beklenen: {test['beklenen_risk']}")
    
    # Analiz yap
    sonuc = evaluator.analiz_yap(test['metin'], profil='hibrit', yas_grubu='10-15')
    
    # Kategoriye ait bulguları bul
    kategori_bulgusu = None
    for kat_key, kat_data in sonuc['kategori_bulgulari'].items():
        if test['kategori'].lower().replace(' ', '_') in kat_key.lower():
            kategori_bulgusu = kat_data
            break
    
    if kategori_bulgusu:
        bulgu_sayisi = kategori_bulgusu.get('toplam_bulgu', 0)
        avg_risk = kategori_bulgusu.get('ortalama_risk', 0) if bulgu_sayisi > 0 else 0
        
        if bulgu_sayisi == 0:
            print(f"   ✅ Bulgu: 0 (Zararsız olarak tespit)")
        else:
            print(f"   ⚠️  Bulgu: {bulgu_sayisi} adet, Ort. Risk: {avg_risk:.2f}/5")
            
            # Detay göster
            for i, bulgu in enumerate(kategori_bulgusu.get('bulunan_kelimeler', [])[:2], 1):
                kelime = bulgu['kelime']
                risk = bulgu['baglamsal_risk']
                kontekst = bulgu.get('kontext', '')[:60]
                print(f"      {i}. \"{kelime}\" (Risk: {risk}/5) - Kontekst: {kontekst}...")
    else:
        print(f"   ✅ Bulgu: 0 - Kategori taraması yok")

print("\n" + "=" * 80)
print("✅ SMART CONTEXT ANALYSIS TESTI TAMAMLANDI")
print("=" * 80)
