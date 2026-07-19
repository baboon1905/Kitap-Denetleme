#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
from evaluator_maarif import MaarifDegerlendiricisi

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

evaluator = MaarifDegerlendiricisi()
sonuc = evaluator.analiz_yap(metin)

# kategori_bulgulari göster
print("kategori_bulgulari:")
for kat, details in sonuc.get("kategori_bulgulari", {}).items():
    print(f"  {kat}: {details.get('toplam_bulgu', 0)}")

# Toplam
toplam = sum(v.get('toplam_bulgu', 0) for v in sonuc.get("kategori_bulgulari", {}).values())
print(f"\nToplam: {toplam}")
