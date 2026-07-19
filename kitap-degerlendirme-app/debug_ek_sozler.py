#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: ek_sozler kontrolleri çalışıyor mu?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi
from config import FALSE_POSITIVE_FILTER

# PDF'i oku
pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

# Metin'de ek_sozler sözcüklerini ara
print("=== EK SOZLER KONTROL ===\n")

for kelime in ["fal", "ayin"]:
    if kelime in FALSE_POSITIVE_FILTER:
        fp = FALSE_POSITIVE_FILTER[kelime]
        if "ek_sozler" in fp and fp["ek_sozler"]:
            print(f"\n{kelime.upper()} - ek_sozler kontrol:")
            for sozcu in fp["ek_sozler"][:5]:  # İlk 5'i göster
                metin_lower = metin.lower()
                if sozcu.lower() in metin_lower:
                    count = metin_lower.count(sozcu.lower())
                    print(f"  ✓ '{sozcu}' found {count} times")
                else:
                    print(f"  ✗ '{sozcu}' NOT found")
        else:
            print(f"\n{kelime.upper()} - ek_sozler BOŞ!")

# Analiz et
print("\n=== ANALIZ SONUCU ===")
evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# Sayıları göster
toplam = sum(len(v) for v in sonuc.values() if isinstance(v, list))
print(f"\nToplam bulgu: {toplam}")

# "fal" ve "ayin" bul
fal_count = 0
ayin_count = 0
for kat, bulgular in sonuc.items():
    if isinstance(bulgular, list):
        for bulgu in bulgular:
            if bulgu.get("kelime") == "fal":
                fal_count += 1
            if bulgu.get("kelime") == "ayin":
                ayin_count += 1

print(f"'fal' findings: {fal_count}")
print(f"'ayin' findings: {ayin_count}")
