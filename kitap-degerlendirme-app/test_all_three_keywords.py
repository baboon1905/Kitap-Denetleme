#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test: "vur", "gökkuşağı", "ayıp" keyword'lerinin BERABER doğru çalışması
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni - Üç keyword'ü içeren gerçekçi metin
test_metin = """
Çocuğun kitabında güzel bir gökkuşağı resmi vardı. Gökkuşağı renkleri çok canlı idi.
Resimde kuş, çiçek ve ağaçlar da bulunuyordu. Bir masala hikâyesi anlatan bu ressam
eseri, çocukların sevdiği sanatçı tarafından yapılmıştı.

Ama bazı sahnelerde vurdu, vurmaya çalıştı. Şiddet sahnesi vardı.
Vuruyor, vurduktan sonra kaçıyor. Karakterin vuruş hareketleri çok açıktı.

Çocuk katlayıp başlayıp kitabını aldı. Ancak, ayıp bir davranış yapıyordu.
Gerçekten ayıp şekilde konuştu. Bu ayıp bir olay olmuş.
"""

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(test_metin)

print("\n" + "="*70)
print("TEST SONUÇLARI: 'vur', 'gökkuşağı', 'ayıp' Keyword'leri")
print("="*70)

for kategori_adi, kategori_bulgular in sonuc["kategori_bulgulari"].items():
    if kategori_bulgular["bulundu"]:
        print(f"\n✅ KATEGORİ: {kategori_adi}")
        print(f"   Toplam bulgu: {kategori_bulgular['toplam_bulgu']}")
        
        for bulgu in kategori_bulgular['bulunan_kelimeler']:
            risk_status = "✓ VALID" if bulgu['baglamsal_risk'] > 0 else "○ FILTERED"
            print(f"   • '{bulgu['kelime']}' (Risk: {bulgu['baglamsal_risk']}/5) {risk_status}")

print("\n" + "="*70)
print(f"GENEL RİSK SKORU: {sonuc['final_skor']:.1f}/100")
print("="*70)

# Özet
toplam = sum(k['toplam_bulgu'] for k in sonuc['kategori_bulgulari'].values())
print(f"\n📊 Özet: {toplam} bulgu tespit edildi")

print("\n🎯 Beklenen Sonuçlar:")
print("  ✓ 'gökkuşağı' → Risk: 0/5 (harmless pattern)")
print("  ✓ 'vur' (vuruş sahnesi) → Risk: 3-4/5")
print("  ✓ 'ayıp' (gerçek kullanım) → Risk: 4/5")
print("  ✓ Verb conjugation'lar (vurmaya, katlayıp, başlayıp) → Filtered")
