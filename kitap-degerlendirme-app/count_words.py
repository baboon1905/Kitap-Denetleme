#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

# Metin'de geçiş sayıları
metin_lower = metin.lower()

print(f"'fal' count: {metin_lower.count('fal')}")
print(f"'ayin' count: {metin_lower.count('ayin')}")
print(f"'kan' count: {metin_lower.count('kan')}")
print(f"'ölüm' count: {metin_lower.count('ölüm')}")
print(f"'büyü' count: {metin_lower.count('büyü')}")
