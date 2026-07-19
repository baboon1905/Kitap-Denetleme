"""
TEST: PDF İçeriğinden Metin Çıkarıp Analiz Etme
"""
from evaluator_maarif import MaarifDegerlendiricisi

# PDF'den çıkarılan metin örnekleri
pdf_metinler = {
    "Sihirli Duduk": """
    Serkan henüz üçüncü sınıfta. Sınıfın en çalışkanı. En güzel resim yapanı.
    Üstelik okul korosunda da en güzel şarkı söyleyen o. Yine de çok mutsuz.
    Çünkü bir türlü futbol oynamayı başaramıyor.
    
    O yıl okula yeni gelmişti. Önce kendini sınıfta çok yabancı hissetti, ama sonra 
    birçok arkadaş edindi. Ancak iş maç yapmaya gelince tek başına kalıveriyor.
    
    Ders aralarında tüm arkadaşları hemen okulun sahasına koşuyorlar. O da peşlerinden.
    Takımlara ayrılıyorlar. O da hevesleniyor. Takımlardan birine seçilmek için can atıyor, 
    ama kimse onu çağırmıyor. Bir kenarda oturup oyunu izlemekle yetiniyor.
    
    Derken top havalandı. Serkan'ın başına çarptı. Sonra ayağının dibine yuvarlandı.
    """,
    
    "Panki Karda": """
    Panki, bembeyaz tüylerini yalamayı bıraktı. Gözü, pencereye takıldı. Havada 
    savrulan beyaz noktaları ilk kez görüyordu. Sanki gökyüzünü kelebekler doldurmuştu.
    
    Havalandı sabahın erken saatinde. Serkan oradaydı. Gözünden hiçbir şey kaçmıyordu.
    Buz gibi karların üzerinde yürümek pek de kolay değildi. Patileri ıslandıkça 
    tiksiniyordu. Yine de özgürlüğünden vazgeçmek istemiyordu. Parka doğru ilerledi.
    
    Çalışkan çocuklar oynuyordu. Kar tanelerini yakalamaya çalışıyordu. Yavaşlan dedi,
    havalandı kedi, yuvarlandı kar üzerinde.
    """
}

evaluator = MaarifDegerlendiricisi()

print("=" * 70)
print("📚 PDF İÇERİĞİ ANALİZ TESTİ")
print("=" * 70)

for kitap_adi, metin in pdf_metinler.items():
    print(f"\n📖 {kitap_adi}")
    print("-" * 70)
    
    sonuc = evaluator.analiz_yap(metin, profil='hibrit')
    
    print(f"📊 Final Skor: {sonuc['final_skor']}/100")
    print(f"🎯 Karar: {sonuc['karar']['seviye']}")
    
    toplam_bulgu = sum(sonuc['kategori_bulgulari'][k]['toplam_bulgu'] 
                      for k in sonuc['kategori_bulgulari'])
    
    print(f"🔍 Toplam Bulgu: {toplam_bulgu}")
    
    # Detaylı bulgular
    for kategori, bulgu_data in sonuc['kategori_bulgulari'].items():
        if bulgu_data['bulundu']:
            print(f"\n   📋 {kategori}: {bulgu_data['toplam_bulgu']} bulgu")
            for i, bulgu in enumerate(bulgu_data['bulunan_kelimeler'][:3], 1):
                print(f"      {i}. '{bulgu['kelime']}' → Risk: {bulgu['baglamsal_risk']}/5")
                print(f"         Kontekst: {bulgu['kontext'][:50]}...")

print("\n" + "=" * 70)
print("✅ TEST TAMAMLANDI")
print("=" * 70)
