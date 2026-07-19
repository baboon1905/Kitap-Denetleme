"""
TEST: Kelime Bağımsızlık Kontroller

Veriler: "Ceylan" - "lan" kelimesini içeriyor
Beklenen: 🚫 FALSE POSITIVE (geçersiz bulgu)

Sistem, kelimenin bağımsız olup olmadığını kontrol etmeli
"""

from evaluator_maarif import MaarifDegerlendiricisi

# Test veri
test_metinler = [
    {
        "metin": "Ceylan bahçede oynuyordu.",
        "beklenen": "FALSE POSITIVE",
        "aciklama": "'Ceylan' isiminin içinde 'lan' geçiyor"
    },
    {
        "metin": "Buraya lan, çık dışarıya!",
        "beklenen": "VALID FINDING",
        "aciklama": "'lan' bağımsız bir söz"
    },
    {
        "metin": "Havalandı sabahın erken saatinde.",
        "beklenen": "FALSE POSITIVE",
        "aciklama": "'havalandı' kelimesinin içinde 'lan'"
    },
    {
        "metin": "Serkan ve Hülya geldi.",
        "beklenen": "FALSE POSITIVE",
        "aciklama": "'Serkan' isiminin içinde 'kan' geçiyor"
    },
    {
        "metin": "Yayınevi kitapları basıyor.",
        "beklenen": "FALSE POSITIVE",
        "aciklama": "'yayınevi' kelimesinin içinde 'ayin' geçiyor"
    },
    {
        "metin": "Şeytani ayin yapıyorlarmış.",
        "beklenen": "VALID FINDING",
        "aciklama": "'ayin' bağımsız ve zararlı bağlamda"
    },
]

# Değerlendiriciyi başlat
print("=" * 70)
print("🧪 KELIME BAĞIMSIZLIK KONTROL TESTİ")
print("=" * 70)

evaluator = MaarifDegerlendiricisi()

for i, test in enumerate(test_metinler, 1):
    print(f"\n📌 Test {i}: {test['aciklama']}")
    print(f"   Metin: '{test['metin']}'")
    print(f"   Beklenen: {test['beklenen']}")
    
    # Analiz yap
    sonuc = evaluator.analiz_yap(test['metin'], profil='hibrit')
    
    # Sonuçları göster
    print(f"\n   ✅ Final Skor: {sonuc['final_skor']}/100")
    print(f"   📊 Karar: {sonuc['karar']}")
    
    # Bulgular
    toplam_bulgu = sum(sonuc['kategori_bulgulari'][k]['toplam_bulgu'] 
                      for k in sonuc['kategori_bulgulari'])
    print(f"   🔍 Toplam Bulgu: {toplam_bulgu}")
    
    # Detaylı bulgular
    for kategori, bulgu_data in sonuc['kategori_bulgulari'].items():
        if bulgu_data['bulundu']:
            print(f"\n   📋 Kategori: {kategori}")
            for bulgu in bulgu_data['bulunan_kelimeler']:
                print(f"      • Kelime: '{bulgu['kelime']}'")
                print(f"        Risk: {bulgu['baglamsal_risk']}/5")
                print(f"        Kontekst: {bulgu['kontext']}")

print("\n" + "=" * 70)
print("✅ TEST TAMAMLANDI")
print("=" * 70)
