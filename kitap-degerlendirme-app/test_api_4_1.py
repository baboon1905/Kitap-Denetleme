"""
API üzerinden 4.1 bölümünü test et - Basit metin analizi
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi
from report_generator import RaporOlusturucu

# Alisin Öfkesi'nden örnek metin
test_metin = """
Alisin Öfkesi

Bir zamanlar, çok uzak bir diyarda, adı Alisin olan bir kız yaşıyordu. Alisin çocuk yaşlarından 
beri çok kızgın bir yapıya sahipti. Her küçük şey onu öfkelendirir, her zorluk karşısında hayal kırıklığına 
uğrardı. Ailesi onu sakinleştirmeye çalışsa da Alisin'in öfkesi hiç dinmiyordu.

Bir gün, köyün yaşlı dede onu çağırdı. "Alisin," dedi, "senin öfken kimseye yararı yok. Ne kendine ne 
başkasına. Öfkenin sana yol göstermesine izin verme, sen öfkeni yönet. Akıl ve sabır, aile değerlerine 
saygı, kardeşliğin kıymetini bil. Vatan ve millet için çalış, insanlara karşı dürüst ol."

Alisin çok şaşırdı. Yaşlı dedenin sözleri onda derin bir etki bıraktı. Bundan sonra, her kızıştığında 
dedenin sözlerini hatırladı. Savaşıp dişlemek yerine, sabretti. Insanları anlama çabası gösterdi. 
Ailesi ile ilgilenmeye başladı. Vatan sevgisini, erdem ve ahlak değerlerini benimsedi.

Zamanla Alisin'in öfkesi taa dağlar kadar düştü. Herkes onu sevir başladı. Dedesinden aldığı dersleri 
başka çocuklara da öğretti. Böylece köy barış ve huzurla doldu. Alisin da çocuksu öfkesini ardında bırakıp, 
bir akılll ve sorumluluk sahibi genç kız oldu.

Masaldan çıkaracak ders: Öfke kötü bir danışman, akıl ise iyi bir rehberdir. Aile değerlerini, 
kardeşliği, vatanı sev. Dürüstlük ve erdem, hayatın en değerli hazineleridir.
"""

try:
    print("=" * 60)
    print("API Test - 4.1 Bölümü (Direct Python)")
    print("=" * 60)
    
    # Evaluator ile analiz et
    print(f"\n1. Evaluator ile analiz başlatılıyor...")
    evaluator = MaarifDegerlendiricisi()
    analiz_data = evaluator.analiz_yap(test_metin, profil="hibrit", yas_grubu="9-12")
    print(f"   ✅ Analiz tamamlandı")
    
    # MEB değerlendirmesi kontrol et
    print(f"\n2. MEB Değerlendirmesi:")
    meb_eval = analiz_data.get('meb_degerlendirmesi', {})
    
    meb_kriterler = meb_eval.get('meb_kriterler', {})
    print(f"   meb_kriterler: {bool(meb_kriterler)}")
    print(f"   meb_kriterler keys: {list(meb_kriterler.keys()) if meb_kriterler else 'None'}")
    
    if meb_kriterler:
        print(f"   Tüm Kriterler:")
        for kriter_key, kriter_info in meb_kriterler.items():
            risk = kriter_info.get('risk', 0)
            print(f"      {kriter_key}: risk={risk}/5 - {kriter_info.get('karar', 'N/A')}")
    
    meb_bulgulari = meb_eval.get('meb_bulgulari', {})
    print(f"\n   meb_bulgulari: {bool(meb_bulgulari)}")
    print(f"   meb_bulgulari type: {type(meb_bulgulari)}")
    print(f"   meb_bulgulari value: {meb_bulgulari}")
    if meb_bulgulari:
        print(f"   meb_bulgulari.values(): {list(meb_bulgulari.values())}")
        print(f"   any(meb_bulgulari.values()): {any(meb_bulgulari.values())}")
    
    # Rapor oluştur
    print(f"\n3. PDF Rapor oluşturuluyor...")
    rapor_generator = RaporOlusturucu()
    pdf_buffer = rapor_generator.olustur(
        degerlen_sonuclari=analiz_data,
        metadata={'kitap_adi': 'Test-Alisin'}
    )
    
    # PDF'i kaydet
    pdf_buffer.seek(0)
    with open("test_direct_report.pdf", "wb") as f:
        f.write(pdf_buffer.read())
    
    # PDF'in içinde "4.1" var mı kontrol et
    pdf_buffer.seek(0)
    pdf_text = pdf_buffer.read().decode('utf-8', errors='ignore')
    
    # Detaylı kontrol et
    has_4_1_detayli = "4.1 Detayli" in pdf_text
    has_4_1_detaylı = "4.1 Detaylı" in pdf_text
    has_bulgu_analizi = "Bulgu Analizi" in pdf_text
    
    print(f"\n   String arama sonuçları:")
    print(f"     '4.1 Detayli': {has_4_1_detayli}")
    print(f"     '4.1 Detaylı': {has_4_1_detaylı}")
    print(f"     'Bulgu Analizi': {has_bulgu_analizi}")
    
    if has_4_1_detayli or has_4_1_detaylı:
        print(f"\n   ✅ 4.1 BÖLÜMÜ RAPORDA BULUNDU!")
    else:
        print(f"\n   ❌ 4.1 BÖLÜMÜ RAPORDA BULUNAMADI")
    
    print(f"\n4. Rapor kaydedildi: test_direct_report.pdf")
    print("\n" + "=" * 60)

except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
