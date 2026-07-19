# -*- coding: utf-8 -*-
"""
Rapordaki FALSE POSITIVE'leri test et
"""

import sys
sys.path.insert(0, '.')

from evaluator_maarif import MaarifDegerlendiricisi

# Rapordaki kelimeleri test et
test_cases = [
    ("ölümü", "radyo Televizyon ve Sinema Bölümünden mezun oldu. 2001 yılından bu yana", "Should filter (Bölüm)"),
    ("ölümün", "radyo Televizyon ve Sinema Bölümünden mezun oldu. 2001 yılından bu yana", "Should filter (Bölüm)"),
    ("ayıp", "Çok ayıp olur. ilişkimiz daha yeni başladı.", "Should NOT filter (gerçek ayıp)"),
]

print("=" * 80)
print("📊 RAPOR FALSE POSITIVE TEST")
print("=" * 80)

for kelime, metin, beklenen in test_cases:
    print(f"\n🔍 Kelime: '{kelime}'")
    print(f"   Metni: {metin[:60]}...")
    print(f"   Beklenen: {beklenen}")
    
    try:
        evaluator = MaarifDegerlendiricisi()
        sonuc = evaluator.analiz_yap(metin, profil='maarif_meb')
        
        # Kategorileri kontrol et
        kategori_bulgulari = sonuc.get('kategori_bulgulari', {})
        
        bulundu = False
        for kategori, veri in kategori_bulgulari.items():
            for item in veri.get('bulunan_kelimeler', []):
                if item['kelime'] == kelime:
                    bulundu = True
                    print(f"   ✅ RAPOR EDİLDİ: {kategori} (Risk={item['baglamsal_risk']}/5)")
        
        if not bulundu:
            print(f"   🚫 FİLTRELENDİ (Rapor edilmedi)")
            
    except Exception as e:
        print(f"   ❌ Hata: {e}")

print("\n" + "=" * 80)
print("ÖNEMLİ: Eğer 'ölümü' ve 'ölümün' rapor edildiyse = SORUN VAR")
print("=" * 80)
