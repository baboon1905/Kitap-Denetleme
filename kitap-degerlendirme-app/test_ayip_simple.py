#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: Sadece gerçek "ayıp" kullanımını test et
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni - SADECE gerçek "ayıp" kullanımı
test_metin = """
Bu ayıp bir davranış. Ayıp şekilde konuştu.
"""

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(test_metin)

print("\n" + "="*60)
print("TEST: SADECE GERÇEK 'ayıp' KULLANIMI")
print("="*60)

for kategori_adi, kategori_bulgular in sonuc["kategori_bulgulari"].items():
    if kategori_bulgular["bulundu"]:
        print(f"\n✅ KATEGORİ: {kategori_adi}")
        print(f"   Bulgu sayısı: {kategori_bulgular['toplam_bulgu']}")
        for bulgu in kategori_bulgular['bulunan_kelimeler']:
            print(f"   - '{bulgu['kelime']}' (Risk: {bulgu['baglamsal_risk']}/5)")
            print(f"     Kontekst: {bulgu['kontext'][:100]}...")

print("\n" + "="*60)
print(f"GENEL RİSK SKORU: {sonuc['final_skor']:.2f}/100")
print("="*60)
