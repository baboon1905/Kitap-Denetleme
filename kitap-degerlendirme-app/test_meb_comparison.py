# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi

# Test 1: Sadece FALSE POSITIVE'ler
metin1 = 'Kargo alımı yapıldı. Pazar günü kargo geldi. Market açılıyor.'

# Test 2: TRUE POSITIVE + FALSE POSITIVE'ler
metin2 = 'Kargo alımı yapıldı. Argo konuşuyor. Market açılıyor.'

testler = [
    ("Test 1: Sadece FALSE POSITIVE (kargo, market)", metin1),
    ("Test 2: TRUE POSITIVE + FALSE POSITIVE (argo + kargo)", metin2),
]

for test_adi, metin in testler:
    print("\n" + "=" * 80)
    print(f"📊 {test_adi}")
    print("=" * 80)
    
    try:
        evaluator = MaarifDegerlendiricisi()
        sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
        
        meb = sonuc.get('meb_degerlendirmesi', {})
        meb_bulgulari = meb.get('meb_bulgulari', {})
        
        print(f"\n✓ MEB Bulguları:")
        if meb_bulgulari:
            toplam = sum(len(v) for v in meb_bulgulari.values())
            print(f"  Toplam: {toplam} bulgu")
            for kriter, bulgular_list in meb_bulgulari.items():
                if bulgular_list:
                    print(f"  - {kriter}: {len(bulgular_list)} bulgu")
        else:
            print("  ✓ TEMIZ - Hiç bulgu yok!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
