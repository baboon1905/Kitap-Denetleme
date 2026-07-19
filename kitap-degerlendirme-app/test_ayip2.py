#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evaluator_maarif import MaarifDegerlendiricisi

metin = """
Konuşmayı bırakıp annesiyle dayanamayıp gülmeye başlayan bir çocuk.
Tutamayıp düştü. Anlamayıp sordu.
"""

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# ayıp bulgularını göster
print("ayıp findings:")
for kat, bulgular in sonuc.items():
    if isinstance(bulgular, list):
        for bulgu in bulgular:
            if bulgu.get("kelime") == "ayıp":
                print(f"  {bulgu}")

# Toplam
toplam = sum(len(v) for v in sonuc.values() if isinstance(v, list))
print(f"\nToplam: {toplam}")
