# -*- coding: utf-8 -*-
"""
FALSE POSITIVE Filtreleme Test - Gerçek Rapor Benzeri
Sistem tüm FALSE POSITIVE'leri filtreliyor mu kontrol et
"""

import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi
import json

# Tipik FALSE POSITIVE'ler içeren metin
metin = '''
Kitap Adı: Ceylan ve Serkan'ın Macerası

Bölüm 1: Tanışma

Ceylan çok güzel bir kızydı. Serkan ise mütercim tercümandı. 
Müzede havalandı salon. Büyükbabası müze müdürüydü.
Yayınevi tarafından basılan kitap çok başarılı olmuştu.

Bölüm 2: Sorunlar

Sigara içmenin zararlı olduğu bilinen bir gerçektir.
Ama karakterimiz sigaranın tadı güzeldi diyordu.
Alkol tüketimi de aynı şekilde zararlıdır.

Katlayıp tuttuğu kağıtta önemli bilgiler vardı.
Kahkaha atmaya başlayıp yere düştü.
Çadır kurup orada uyuduk.
'''

print("=" * 80)
print("📊 GERÇEK RAPOR BENZERI TEST")
print("=" * 80)

try:
    evaluator = MaarifDegerlendiricisi()
    sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
    
    # Kategori bulgularını kontrol et
    kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
    
    print("\n📋 RAPOR EDILEN BULGULAR:\n")
    
    toplam_bulgu = 0
    for kategori, veri in kategori_bulgulari.items():
        if veri.get('toplam_bulgu', 0) > 0:
            toplam_bulgu += veri['toplam_bulgu']
            print(f"\n🔴 {kategori.upper()}")
            print(f"   Bulgu Sayısı: {veri['toplam_bulgu']}")
            
            for i, item in enumerate(veri['bulunan_kelimeler'], 1):
                kelime = item['kelime']
                risk = item['baglamsal_risk']
                kontekst = item['kontext'][:80]
                
                print(f"\n   {i}. Kelime: '{kelime}' (Risk: {risk}/5)")
                print(f"      Bağlam: {kontekst}...")
    
    print("\n" + "=" * 80)
    print(f"📊 TOPLAM BULGULAR: {toplam_bulgu}")
    print(f"📈 FINAL SKOR: {sonuc.get('final_skor', 0):.0f}/100")
    
    # FALSE POSITIVE adayları
    print("\n" + "=" * 80)
    print("⚠️  Kontrol Et (FALSE POSITIVE mi?):")
    print("=" * 80)
    print("""
    - 'lan' kelimesi: Ceylan, havalandı → Filtrelenmeli
    - 'kan' kelimesi: Serkan → Filtrelenmeli
    - 'ölüm' kelimesi: Bölüm → Filtrelenmeli
    - 'ayıp' kelimesi: katlayıp, başlayıp → Filtrelenmeli
    - 'büyü' kelimesi: büyükbabası → Filtrelenmeli
    """)
    
except Exception as e:
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
