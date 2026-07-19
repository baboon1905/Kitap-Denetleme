#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiz: Sakıncalı kelimeler'in harf uzunluğu dağılımı
Hangi kelimelerin agresif filtre'ye ihtiyacı var?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import SAKINCALI_KELIMELER

# Harf uzunluğuna göre kelimeler'i grupla
uzunluk_dagilim = {}

for kategori, kelimeler in SAKINCALI_KELIMELER.items():
    for kelime in kelimeler:
        uzunluk = len(kelime)
        if uzunluk not in uzunluk_dagilim:
            uzunluk_dagilim[uzunluk] = []
        uzunluk_dagilim[uzunluk].append((kelime, kategori))

print("\n" + "="*70)
print("SAKINCALI KELİMELER - HARF UZUNLUĞU DAĞILIMI")
print("="*70)

for uzunluk in sorted(uzunluk_dagilim.keys()):
    kelimeler = uzunluk_dagilim[uzunluk]
    print(f"\n{uzunluk} Harf ({len(kelimeler)} kelime):")
    
    # Benzersiz kelimeler (kategoriler göz ardı)
    unique_words = sorted(set(k[0] for k in kelimeler))
    
    if uzunluk <= 4:
        # Çok kısa kelimeleri göster (agresif filtre adayı)
        print(f"  ⚠️  AGRESIF FİLTRE ADAYLARI:")
        for kelime in unique_words[:15]:  # İlk 15'i göster
            print(f"     - {kelime}")
        if len(unique_words) > 15:
            print(f"     ... ve {len(unique_words) - 15} daha")
    
print("\n" + "="*70)
print(f"Total: {sum(len(v) for v in uzunluk_dagilim.values())} kelime variant")
print(f"Benzersiz: {sum(len(set(k[0] for k in v)) for v in uzunluk_dagilim.values())} kelime")

# Agresif filtre adayları (3-4 harf)
agresif_candidates = set()
for uzunluk in [3, 4]:
    if uzunluk in uzunluk_dagilim:
        agresif_candidates.update(k[0] for k in uzunluk_dagilim[uzunluk])

print(f"\n🔴 3-4 harfli kelimeler ({len(agresif_candidates)} adet):")
for kelime in sorted(agresif_candidates)[:50]:
    print(f"   {kelime}")

if len(agresif_candidates) > 50:
    print(f"   ... ve {len(agresif_candidates) - 50} daha")
