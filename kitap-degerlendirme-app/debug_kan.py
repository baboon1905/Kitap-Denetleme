#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: "kan" nedir? Hangi isim/verb'den kaynaklanıyor?"""

import os
import sys
from pdf_processor import PDFProcessor
from config import FALSE_POSITIVE_FILTER

# PDF dosyasını oku
pdf_path = "uploads/10_sihirli_duduk.pdf"
processor = PDFProcessor(pdf_path)
metin = processor.extract_text()
metin_normalized = metin.lower()

print("=" * 70)
print("🔍 DEBUG: 'kan' neden geçiyor?")
print("=" * 70)

# FALSE_POSITIVE_FILTER'de "kan" için tanımlanan isimler/verbler
kan_fp = FALSE_POSITIVE_FILTER.get("kan", {})

print("\n1️⃣ Metin'de 'Serkan' var mı?")
if "serkan" in metin_normalized:
    print(f"   ✅ VAR! Index: {metin_normalized.find('serkan')}")
    idx = metin_normalized.find("serkan")
    print(f"   Context: ...{metin_normalized[max(0, idx-20):min(len(metin_normalized), idx+30)]}...")
else:
    print("   ❌ YOK")

print("\n2️⃣ Metin'de 'Erkan' var mı?")
if "erkan" in metin_normalized:
    print(f"   ✅ VAR! Index: {metin_normalized.find('erkan')}")
    idx = metin_normalized.find("erkan")
    print(f"   Context: ...{metin_normalized[max(0, idx-20):min(len(metin_normalized), idx+30)]}...")
else:
    print("   ❌ YOK")

print("\n3️⃣ Metin'de 'Furkan' var mı?")
if "furkan" in metin_normalized:
    print(f"   ✅ VAR!")
else:
    print("   ❌ YOK")

print("\n4️⃣ Tüm 'kan' isimleri kontrol et:")
if "turkce_isimler" in kan_fp:
    for isim in kan_fp["turkce_isimler"]:
        if isim.lower() in metin_normalized:
            print(f"   ✅ '{isim}' → FOUND")

print("\n5️⃣ Tüm 'kan' verb'leri kontrol et:")
if "ek_sozler" in kan_fp:
    for verb in kan_fp["ek_sozler"]:
        if verb.lower() in metin_normalized:
            print(f"   ✅ '{verb}' → FOUND")

# "kan" raw olarak nerede geçiyor?
print("\n6️⃣ 'kan' solo occurrences (space'ler ile):")
import re
pattern = r'\bkan\b'  # Word boundary
matches = list(re.finditer(pattern, metin_normalized, re.IGNORECASE))
print(f"   Bulunan: {len(matches)} adet")
for i, match in enumerate(matches[:5]):
    idx = match.start()
    print(f"   {i+1}. ...{metin_normalized[max(0, idx-15):min(len(metin_normalized), idx+20)]}...")

print("\n" + "=" * 70)
