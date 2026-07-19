# -*- coding: utf-8 -*-
import sys
import json
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni - riskli kelimeler içeren
metin = '''
Adım Ceylan. Arkadaşım Serkan. Sigaranın tadı güzel.
'''

try:
    evaluator = MaarifDegerlendiricisi()
    sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
    
    # Kategori bulgularını kontrol et
    kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
    
    print("=" * 80)
    print("ZARARLÍ ALIŞKANLÍKLAR KATEGORİSİ:")
    print("=" * 80)
    
    if 'zararlı_alışkanlıklar' in kategori_bulgulari:
        veri = kategori_bulgulari['zararlı_alışkanlıklar']
        print(f"Bulundu: {veri.get('bulundu')}")
        print(f"Toplam bulgu: {veri.get('toplam_bulgu')}")
        print(f"Ortalama risk: {veri.get('ortalama_risk')}")
        
        if veri.get('bulunan_kelimeler'):
            print("\nBulunan Kelimeler:")
            for item in veri['bulunan_kelimeler']:
                print(f"  - Kelime: {item['kelime']}")
                print(f"    Risk: {item['baglamsal_risk']}")
                print(f"    Kontekst: {item['kontext']}")
    
    print("\n" + "=" * 80)
    print("MEB DEĞERLENDİRMESİ:")
    print("=" * 80)
    meb = sonuc.get('meb_degerlendirmesi', {})
    print(json.dumps({k: v for k, v in meb.items() if k != 'meb_bulgulari'}, 
                     ensure_ascii=False, indent=2))
    
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
