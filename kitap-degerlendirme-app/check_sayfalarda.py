#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

pdf_path = "uploads/Anahtar_Acmaz.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

# "sayfalarda" veren bağlamları göster
lines = metin.split('\n')
for i, line in enumerate(lines):
    if 'sayfalarda' in line.lower() or 'sayfalar' in line.lower():
        print(f"Line {i}: {line[:100]}")
