#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi

# Test 1: defalarca'da fal
metin = "defalarca gördü ve sonra fal"

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# kategori_bulgulari göster
print("Test: 'defalarca gördü ve sonra fal'")
print("kategori_bulgulari:")
for kat, details in sonuc.get("kategori_bulgulari", {}).items():
    print(f"  {kat}: {details.get('toplam_bulgu', 0)}")

print(f"\nSonuc keys: {list(sonuc.keys())}")



