#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Kontrol etme logic'i test et
"""

from pdf_processor import PDFProcessor
from config import FALSE_POSITIVE_FILTER

pdf_path = r"uploads\10_sihirli_duduk.pdf"

print("=" * 70)
print("🔍 DEBUG: Verb Conjugation Matching Test")
print("=" * 70)

# PDF metin'i al
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()
metin_normalized = metin.lower()

# Test: "kan" için "çalışkan" match et
print("\n1️⃣ Test: 'kan' içinde 'çalışkan' var mı?")
word_to_find = "kan"
context_word = "çalışkan"

print(f"   Metin'de '{context_word}' var mı? {context_word in metin_normalized}")

if context_word in metin_normalized:
    pos = metin_normalized.find(context_word)
    print(f"   Bulundu! Position: {pos}")
    print(f"   Kelime: {metin_normalized[pos:pos+len(context_word)]}")
    
    # "kan" pozisyonlarını bul
    kan_pos = 0
    kan_count = 0
    while True:
        kan_pos = metin_normalized.find(word_to_find, kan_pos)
        if kan_pos == -1:
            break
        
        # Bu "kan" context_word'ün içinde mi?
        context_start = pos
        context_end = pos + len(context_word)
        
        if context_start <= kan_pos < context_end:
            print(f"   ✅ 'kan' bu konumda EMBEDDED: position {kan_pos}")
            # Now check before character
            if kan_pos > 0:
                before_char = metin_normalized[kan_pos - 1]
                print(f"      Öncesi: '{before_char}' (isalpha={before_char.isalpha()})")
            break
        
        kan_pos += 1

# Test 2: "havalandı" match et
print("\n2️⃣ Test: 'lan' içinde 'havalandı' var mı?")
verb_word = "havalandı"
target_word = "lan"

if verb_word in metin_normalized:
    print(f"   ✅ '{verb_word}' bulundu metin'de")
    verb_pos = metin_normalized.find(verb_word)
    
    # "lan" pozisyonlarını bul
    lan_pos = 0
    while True:
        lan_pos = metin_normalized.find(target_word, lan_pos)
        if lan_pos == -1:
            break
        
        verb_start = verb_pos
        verb_end = verb_pos + len(verb_word)
        
        if verb_start <= lan_pos < verb_end:
            print(f"   ✅ 'lan' embedded in '{verb_word}' @ position {lan_pos}")
            print(f"      Position in word: {lan_pos - verb_start}")
            break
        
        lan_pos += 1
else:
    print(f"   ❌ '{verb_word}' NOT found")

print("\n" + "=" * 70)
