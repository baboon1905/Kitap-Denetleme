#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: Check 'gökkuşağı' text extraction and search"""

import sys
sys.path.insert(0, '.')

from pdf_processor import PDFProcessor

pdf_path = "uploads/alisin_ofkesi_5.basim.pdf"

processor = PDFProcessor(pdf_path)
metin = processor.extract_text()

print("=" * 70)
print("DEBUG: 'gökkuşağı' Search")
print("=" * 70)

# Raw search
print(f"\n1. Raw text search (case-sensitive):")
idx = metin.find("gökkuşağı")
print(f"   'gökkuşağı' position: {idx}")

idx2 = metin.find("Gökkuşağı")
print(f"   'Gökkuşağı' position: {idx2}")

idx3 = metin.find("gökkuşağ")
print(f"   'gökkuşağ' (partial) position: {idx3}")

# With context
if idx3 != -1:
    context_start = max(0, idx3 - 50)
    context_end = min(len(metin), idx3 + 100)
    context = metin[context_start:context_end]
    print(f"   Context: ...{context}...\n")
    print(f"   Raw bytes: {repr(metin[idx3:idx3+20])}")

# Normalized search
print(f"\n2. Normalized text search (lowercase):")
metin_lower = metin.lower()

# Try different variations
variations = [
    "gökkuşağı",
    "gökküsağı",
    "gokkusagi",
    "gökkusağı",
    "gokkuşağı"
]

for var in variations:
    count = metin_lower.count(var)
    pos = metin_lower.find(var)
    if count > 0:
        print(f"   ✅ '{var}': {count} occurrences (pos: {pos})")
        context_start = max(0, pos - 50)
        context_end = min(len(metin_lower), pos + 100)
        context = metin_lower[context_start:context_end]
        print(f"       Context: ...{context}...\n")

# Unicode check
print(f"\n3. Unicode analysis:")
if idx3 != -1:
    word = metin[idx3:idx3+20]
    print(f"   Word: {word}")
    print(f"   Codepoints: {[hex(ord(c)) for c in word[:10]]}")
    
    word_lower = word.lower()
    print(f"   Lowercased: {word_lower}")
    print(f"   Lower codepoints: {[hex(ord(c)) for c in word_lower[:10]]}")
