# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi

# Kapsamlı FALSE POSITIVE test metni
metin = '''
Adım Ceylan, arkadaşım Serkan. Müze ziyareti yaptı.
Havalandı bahçe. Katlayıp kağıdı aldı. 
Büyükbabam geldi. Yayınevim başarılı kitap yayımlıyor.
Bölüm 1 tamamlandı. Yayınevi markası ünlü.
Kahkaha atmaya başlayıp kılıçla savaştı.
Çadır kurup uyuduk. Şiddet sahnesi var.
Sigara içmek zararlıdır. Alkol tüketilmemeli.
'''

try:
    evaluator = MaarifDegerlendiricisi()
    sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
    
    kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
    
    print('=' * 80)
    print('📊 KAPSAMLı SONUÇLAR:')
    print('=' * 80)
    
    toplam_bulgu = 0
    for kategori, veri in kategori_bulgulari.items():
        if veri.get('toplam_bulgu', 0) > 0:
            toplam_bulgu += veri['toplam_bulgu']
            print(f"\n✓ {kategori}: {veri['toplam_bulgu']} bulgu")
            for item in veri['bulunan_kelimeler'][:5]:  # İlk 5'i göster
                print(f"    - {item['kelime']}: {item['kontext'][:60]}...")
    
    print('\n' + '=' * 80)
    print(f'📈 TOPLAM RISKLI BULGU: {toplam_bulgu}')
    print(f'📊 FINAL SKOR: {sonuc.get("final_skor", 0):.0f}/100')
    print(f'🎯 KARAR: {sonuc.get("karar", "N/A")}')
    print('=' * 80)
    
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
