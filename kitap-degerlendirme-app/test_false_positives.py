# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi
from config import *

# Test metni - riskli kelimeler içeren ama başka kelimelerin içinde
metin = '''
Adım Ceylan. Arkadaşım Serkan. Kitabımız yayınevi tarafından basıldı.
Havalandı bahçe. Katlayıp kağıdı aldı. Kahkaha atmaya başladı.
Sigaranın tadı güzel. Deneyin bunu. Kahraman erkek sigara içerken vurgulandı.
Alkol içerek eğlendi. Bahis oynarken kaybetti.
'''

try:
    evaluator = MaarifDegerlendiricisi()
    sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
    
    print('=' * 80)
    print('SONUÇ YAPISI:')
    print('=' * 80)
    print(f"Sonuç keys: {sonuc.keys()}")
    
    if 'kategori_bulgulari' in sonuc:
        print('\nKATEGORI BULGULARI:')
        for kategori, bulgu_data in sonuc['kategori_bulgulari'].items():
            if isinstance(bulgu_data, dict):
                bulundu = bulgu_data.get('bulundu', False)
                toplam = bulgu_data.get('toplam_bulgu', 0)
                print(f"  {kategori}: bulundu={bulundu}, toplam_bulgu={toplam}")
                if 'bulunan_kelimeler' in bulgu_data and bulgu_data['bulunan_kelimeler']:
                    for item in bulgu_data['bulunan_kelimeler'][:3]:  # İlk 3'ü göster
                        print(f"    - {item['kelime']}: risk={item['baglamsal_risk']}")
    
    print('\n' + '=' * 80)
    print('RISKLI BULGULAR:')
    print('=' * 80)
    
    for kategori, bulgular in sonuc.get('bulgular', {}).items():
        if bulgular:
            print(f'\n{kategori}:')
            for bulgu in bulgular:
                print(f'  - {bulgu}')
    
    print('\n' + '=' * 80)
    print(f'TOPLAM PUAN: {sonuc.get("puan", "N/A")}/100')
    print('=' * 80)
    
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
