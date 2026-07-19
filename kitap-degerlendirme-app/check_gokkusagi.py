#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
from config import FALSE_POSITIVE_FILTER

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

metin_lower = metin.lower()

print(f"'gökkuşağı' count: {metin_lower.count('gökkuşağı')}")

# FALSE_POSITIVE_FILTER'da "gökkuşağı" var mı?
if "gökkuşağı" in FALSE_POSITIVE_FILTER:
    fp = FALSE_POSITIVE_FILTER["gökkuşağı"]
    print(f"FALSE_POSITIVE_FILTER['gökkuşağı']: {fp}")
else:
    print("'gökkuşağı' FALSE_POSITIVE_FILTER'da YOK")
