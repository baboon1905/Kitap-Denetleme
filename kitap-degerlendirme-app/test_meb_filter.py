# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni - MEB kelimeleri
metin = '''
Kargo alım yapıldı. Deneyin bunu. Argo kullanıyor.
Pazar günü kargo geldi. Deneme sırasında...
'''

try:
    evaluator = MaarifDegerlendiricisi()
    sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
    
    print('=' * 80)
    print('MEB BULGULARI (FALSE POSITIVE filtreleme sonrası):')
    print('=' * 80)
    
    meb = sonuc.get('meb_degerlendirmesi', {})
    meb_bulgulari = meb.get('meb_bulgulari', {})
    
    if meb_bulgulari:
        for kriter, bulgular_list in meb_bulgulari.items():
            if bulgular_list:
                print(f"\n{kriter}: {len(bulgular_list)} bulgu")
                for bulgu in bulgular_list:
                    print(f"  - {bulgu.get('sebebi', 'N/A')}")
                    print(f"    Alıntı: {bulgu.get('alininti', 'N/A')[:80]}")
    else:
        print("✓ MEB bulgularında FALSE POSITIVE'ler filtrelendi - Hiç bulgu yok!")
    
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
