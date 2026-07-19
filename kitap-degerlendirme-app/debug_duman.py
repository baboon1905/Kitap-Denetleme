#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: "duman" ve "dumanla" substring matching kontrol
"""

kelime = "duman"
sozcu = "dumanla"

kelime_lower = kelime.lower()
sozcu_lower = sozcu.lower()

print(f"Kelime: '{kelime}' ({len(kelime)} harf)")
print(f"Sözcük: '{sozcu}' ({len(sozcu)} harf)")
print()

# Substring matching kontrol
print(f"len('{sozcu}') > len('{kelime}'):", len(sozcu) > len(kelime))
print(f"'{kelime_lower}' in '{sozcu_lower}':", kelime_lower in sozcu_lower)
print()

# Kontrol1: "duman" SAKINCALI_KELIMELER'de kaç kere var
from config import SAKINCALI_KELIMELER

count = 0
for kategori, kelimeler in SAKINCALI_KELIMELER.items():
    for k in kelimeler:
        if k.lower() == "duman" or k.lower() == "dumanla":
            count += 1
            print(f"✓ Bulundu: '{k}' in {kategori}")

print(f"\nToplam: {count} adet")
