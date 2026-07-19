# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni - başka kelimelerin içinde geçen kelimeler + gerçekten riskli kelimeler
metinler = {
    "Test 1: Sadece Yanlış Pozitifler": '''
    Adım Ceylan. Arkadaşım Serkan. Müze ziyareti. Havalandı bahçe.
    Katlayıp kağıdı aldı. Büyükbabanız geldi. Yayınevim başarılı.
    Bölüm 1 bitmiş.
    ''',
    
    "Test 2: Gerçekten Riskli + Yanlış Pozitifler": '''
    Adım Ceylan. Sigaranın tadı güzel.
    Arkadaşım Serkan. Alkol içerek eğlendi.
    Deneyin bunu. Kahraman erkek sigara içerken vurgulandı.
    ''',
    
    "Test 3: Sadece Gerçekten Riskli": '''
    Sigaranın tadı güzel ve keyif verici.
    Başla denemek için. Kahraman alkol içiyordu.
    Bahis oynarken kaybetti. Nargile çok güzel.
    '''
}

for test_adi, metin in metinler.items():
    print("\n" + "=" * 80)
    print(f"📊 {test_adi}")
    print("=" * 80)
    
    try:
        evaluator = MaarifDegerlendiricisi()
        sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
        
        kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
        
        toplam_bulgu = sum(v.get('toplam_bulgu', 0) for v in kategori_bulgulari.values())
        print(f"\n📈 Toplam bulgu: {toplam_bulgu}")
        print(f"📊 Final skor: {sonuc.get('final_skor', 'N/A')}/100")
        
        for kategori, veri in kategori_bulgulari.items():
            if veri.get('toplam_bulgu', 0) > 0:
                print(f"\n  {kategori}: {veri['toplam_bulgu']} bulgu")
                for item in veri['bulunan_kelimeler']:
                    print(f"    - {item['kelime']} (risk={item['baglamsal_risk']}, kontekst={item['kontext'][:50]}...)")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("ÖNEMLİ: FALSE POSITIVE'ler standart outputta gösterilir (🚫 FALSE POSITIVE)")
print("=" * 80)
