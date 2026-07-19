#!/usr/bin/env python3
# Direct test of olustur_meb_raporu with API data

import sys
import json

# Get test data
test_data_path = 'test_api_data.json'
try:
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    print(f"✅ Loaded test data from {test_data_path}")
except FileNotFoundError:
    print(f"❌ {test_data_path} not found")
    sys.exit(1)

# Direct test
from meb_basit_raporlayici import MEBBulgularıRaporlayıcı

raporlayici = MEBBulgularıRaporlayıcı(font_regular='SegoeUI', font_bold='SegoeUI-Bold')

print("\n=== Testing olustur_meb_raporu ===")
elements = raporlayici.olustur_meb_raporu(test_data)

print(f"\n✅ olustur_meb_raporu returned {len(elements)} elements")

# Check if 4.1 heading is in elements
four_one_found = False
for i, elem in enumerate(elements):
    try:
        if hasattr(elem, 'text') and '4.1' in str(elem.text):
            print(f"✅ Element {i}: Found 4.1 heading!")
            print(f"   Type: {type(elem).__name__}")
            print(f"   Text: {str(elem.text)[:100]}")
            four_one_found = True
    except:
        pass

if not four_one_found:
    print(f"❌ No 4.1 heading found in {len(elements)} elements")
    print("\nElement types:")
    for i, elem in enumerate(elements):
        print(f"  {i}: {type(elem).__name__}")
