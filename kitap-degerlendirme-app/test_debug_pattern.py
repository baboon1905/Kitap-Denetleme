#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: Harmless pattern kontrolü
"""

import re

cumle = "Gökkuşağı rengindeki kuşlar ağaçta oturuyordu."
cumle_lower = cumle.lower()

# Harmless patterns
harmless_patterns = [
    r'gökkuşağı.*(?:rengi|renginde|görmek|var)',  # Doğal renk tanımı
    r'gökkuşağı.*(?:kuş|çiçek|ağaç)',  # Doğada görülür
]

print(f"Cümle: {cumle}")
print(f"Cümle Lower: {cumle_lower}")
print()

for i, pattern in enumerate(harmless_patterns):
    match = re.search(pattern, cumle_lower)
    print(f"Pattern {i}: {pattern}")
    print(f"  Match: {match}")
    if match:
        print(f"  Matched text: {match.group()}")
    print()
