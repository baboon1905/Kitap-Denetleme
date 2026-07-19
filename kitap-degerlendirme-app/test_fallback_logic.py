#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')

# Simulat the fallback code directly
meb_bulgulari = {}  # Empty like in test_api_flow
meb_kriterler = {
    'anayasa': {'risk': 0, 'karar': 'Uyumlu'},
    'milli_guvenlik': {'risk': 0, 'karar': 'Temiz'},
    'esitlik': {'risk': 0, 'karar': 'Uygun'},
    'milli_manevi': {'risk': 0, 'karar': 'Güçlü'},
    'guvenlik': {'risk': 0, 'karar': 'Uygun'},
    'bilimsel': {'risk': 0, 'karar': 'Doğru'},
    'reklam': {'risk': 0, 'karar': 'Temiz'},
    'dil': {'risk': 1, 'karar': 'Dikkat'}  # This should trigger fallback
}

print("=" * 60)
print("Fallback Logic Test")
print("=" * 60)

print(f"\n1. Initial state:")
print(f"   meb_bulgulari: {meb_bulgulari}")
print(f"   any(meb_bulgulari.values()): {any(meb_bulgulari.values()) if meb_bulgulari else 'N/A'}")

# Check fallback condition
print(f"\n2. Fallback condition check:")
print(f"   meb_bulgulari truthy: {bool(meb_bulgulari)}")
print(f"   any(meb_bulgulari.values()): {any(meb_bulgulari.values())}")
print(f"   Condition (meb_bulgulari and any(...)): {meb_bulgulari and any(meb_bulgulari.values())}")
print(f"   NOT condition: {not (meb_bulgulari and any(meb_bulgulari.values()))}")

# Run fallback
print(f"\n3. Running fallback logic:")
if not (meb_bulgulari and any(meb_bulgulari.values())):
    print(f"   ✅ Fallback triggered!")
    meb_bulgulari = {}
    for kriter_key, kriter_info in meb_kriterler.items():
        risk = kriter_info.get('risk', 0)
        if risk > 0:
            print(f"      - {kriter_key}: risk={risk} → bulgu ekleniyor")
            meb_bulgulari[kriter_key] = [{
                'bulgu': kriter_info.get('karar', 'Uyari'),
                'sebebi': f'Kriter Risk: {risk}/5',
                'alinti': '',
                'sayfa': 0
            }]
else:
    print(f"   ❌ Fallback NOT triggered")

print(f"\n4. After fallback:")
print(f"   meb_bulgulari items: {len(meb_bulgulari)}")
print(f"   meb_bulgulari: {meb_bulgulari}")

# Check render condition
print(f"\n5. Render condition check:")
print(f"   meb_bulgulari truthy: {bool(meb_bulgulari)}")
print(f"   any(meb_bulgulari.values()): {any(meb_bulgulari.values())}")
print(f"   Render condition: {meb_bulgulari and any(meb_bulgulari.values())}")

if meb_bulgulari and any(meb_bulgulari.values()):
    print(f"   ✅ 4.1 section would be rendered")
else:
    print(f"   ❌ 4.1 section would NOT be rendered")

print("\n" + "=" * 60)
