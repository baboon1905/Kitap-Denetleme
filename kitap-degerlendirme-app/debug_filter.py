"""
Debug: False Positive Filtresinin Çalışıp Çalışmadığını Kontrol Et
"""
from evaluator_maarif import MaarifDegerlendiricisi

metin = """Derken top havalandı. Serkan'ın başına çarptı. Sonra ayağının dibine yuvarlandı.
Çalışkan çocuklar oynuyordu."""

print("=" * 70)
print("📋 TEST METNİ:")
print(metin)
print("=" * 70)

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin, profil='hibrit')

print(f"\n📊 SONUÇLAR:")
print(f"   Final Skor: {sonuc['final_skor']}/100")
print(f"   Kategori Sayısı: {sonuc['kategori_sayisi']}")
print(f"   Toplam Bulgu: {sonuc['toplam_bulgu']}")

print(f"\n📋 KATEGORİ DETAYLARI:")
for kategori, bulgu in sonuc['kategori_bulgulari'].items():
    if bulgu['bulundu']:
        print(f"\n   {kategori}:")
        print(f"      - Bulunan: {bulgu['toplam_bulgu']}")
        for b in bulgu['bulunan_kelimeler'][:3]:
            print(f"        * '{b['kelime']}' (Risk: {b['baglamsal_risk']}/5)")

print("\n" + "=" * 70)
print("✅ TEST TAMAMLANDI")
print("=" * 70)
