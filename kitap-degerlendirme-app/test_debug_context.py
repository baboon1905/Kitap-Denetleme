#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug: _cumle_konteksti_analiz_et metodunu test et
"""

import sys
import os
import re
sys.path.insert(0, os.path.dirname(__file__))

# Test - cümle seviyesi kontekst analizi
test_cumle1 = "Gökkuşağı rengindeki kuşlar ağaçta oturuyordu."
test_cumle2 = "Çocuk vurmaya başladı."

cumle_lower = test_cumle1.lower()
kelime = "gökkuşağı"
kategori = "okültizm_batil"
varsayilan_risk = 4

# Harmless patterns for okültizm_batil
harmless_patterns = [
    r'antik\s+(?:ayin|ritüel)',
    r'müzede.*sergilenen',
    r'tarihî.*ayin',
    r'araştırma.*kapsamında',
    r'akademik.*çalışma',
    r'mitoloji.*bağlamında',
    r'arkeoloji',
    r'antropoloji',
    r'kültür.*mirası',
    # ⭐ GÖKKUŞAĞI - Harmless Patterns
    r'gökkuşağı.*(?:rengi|renginde|görmek|var)',  # Doğal renk tanımı
    r'gökkuşağı.*(?:kuş|çiçek|ağaç)',  # Doğada görülür
    r'gökkuşağı.*(?:hikâye|masala|çocuk)',  # Çocuk hikâyeleri
    r'gökkuşağı.*(?:ressam|sanatçı|resim)',  # Sanat bağlamı
    r'gökkuşağı.*(?:bulut|yağmur|güneş)',  # Meteoroloji
    r'gökkuşağı.*(?:kitap|roman|öykü)',  # Edebiyat bağlamı
    r'gökkuşağı.*(?:tasarım|desen|motif)',  # Tasarım elemanı
    r'gökkuşağı\s+(?:çiçeği|kuşu|yolu)',  # Adı taşıyan şeyler
    r'(?:at|bul|gör|ara).*gökkuşağı',  # Bir şey "at/bul/gör" fiili ile
]

print(f"Cümle: {test_cumle1}")
print(f"Cümle Lower: {cumle_lower}")
print(f"Kelime: {kelime}")
print()

matched = False
for i, pattern in enumerate(harmless_patterns):
    match = re.search(pattern, cumle_lower)
    if match:
        print(f"✅ HARMLESS Pattern {i} MATCHED!")
        print(f"   Pattern: {pattern}")
        print(f"   Matched text: {match.group()}")
        matched = True

if not matched:
    print("❌ NO HARMLESS PATTERN MATCHED!")

# Harmful patterns
harmful_patterns = [
    r'şeytani\s+ayin',
    r'kara\s+sihir',
    r'kanlı\s+ayin',
    r'gizli\s+ritüel',
    r'okült\s+(?:ayin|ritüel)',
    r'ayin.*yapma',
    r'adama.*ibadet',
    r'cinlere\s+tazim',
    # ⭐ GÖKKUŞAĞI - Harmful Patterns  
    r'gökkuşağı\s+(?:sembolü|göndermesi|ritüeli|mistik)',  # Sembolik/batıl bağlam
]

print("\nHarmful patterns:")
for i, pattern in enumerate(harmful_patterns):
    match = re.search(pattern, cumle_lower)
    if match:
        print(f"⚠️  HARMFUL Pattern {i} MATCHED!")
        print(f"   Pattern: {pattern}")
