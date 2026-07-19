#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem 48 bulgu nedir? Detaylı analiz
"""

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# Kategoriye göre kelimeleri say
sistem_data = {}
for bulgu in sonuc.get('bulgular', []):
    kat = bulgu.get('kategori')
    kelime = bulgu.get('kelime', '').lower()
    
    if kat not in sistem_data:
        sistem_data[kat] = {}
    
    sistem_data[kat][kelime] = sistem_data[kat].get(kelime, 0) + 1

print("=== SISTEM 48 BULGUSU ===\n")

for kat in sorted(sistem_data.keys()):
    belgeler = sistem_data[kat]
    print(f"{kat}: {sum(belgeler.values())} bulgu")
    
    for kelime in sorted(belgeler.keys(), key=lambda x: -belgeler[x]):
        count = belgeler[x]
        print(f"  • {kelime}: {count}")
    print()
