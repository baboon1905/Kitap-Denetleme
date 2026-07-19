#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script: Directly test meb_basit_raporlayici.py
"""

import sys
sys.path.insert(0, '.')

from meb_basit_raporlayici import MEBBulgularıRaporlayıcı

# Create mock result with risk score
sonuclar = {
    'kitap_adi': 'Test Kitap',
    'meb_degerlendirmesi': {
        'meb_bulgulari': {},  # Empty findings
        'meb_kriterler': {
            'anayasa': {'risk': 0, 'karar': 'Uyari', 'ad': 'Anayasa'},
            'dil': {'risk': 1, 'karar': 'Uyari', 'ad': 'Dil Bilgisi'},
            'bilimsel': {'risk': 0, 'karar': 'Uyari', 'ad': 'Bilimsel'}
        }
    }
}

print("=" * 60)
print("Direct Test: meb_basit_raporlayici")
print("=" * 60)

print("\nInput data:")
print(f"  meb_bulgulari: {sonuclar['meb_degerlendirmesi']['meb_bulgulari']}")
print(f"  meb_kriterler dil.risk: {sonuclar['meb_degerlendirmesi']['meb_kriterler']['dil']['risk']}")

try:
    raporlayici = MEBBulgularıRaporlayıcı()
    print("\n✅ MEBBulgularıRaporlayıcı initialized")
    
    elements = raporlayici.olustur_meb_raporu(sonuclar)
    
    print(f"\n✅ olustur_meb_raporu returned {len(elements)} elements")
    
    # Check if 4.1 heading is in elements
    heading_found = False
    for elem in elements:
        elem_str = str(elem)
        if '4.1' in elem_str or 'Detayli Bulgu' in elem_str:
            heading_found = True
            print(f"\n✅ Found 4.1 heading in elements: {type(elem).__name__}")
            break
    
    if not heading_found:
        print("\n❌ 4.1 heading NOT found in elements")
        print("\nElement types:")
        for i, elem in enumerate(elements):
            print(f"  {i}: {type(elem).__name__}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
