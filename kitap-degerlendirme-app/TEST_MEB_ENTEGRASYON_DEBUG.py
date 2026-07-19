#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEB Bulgu Entegrasyonu - DEBUG TEST
"""

# Doğrudan meb_entegrasyon'u test et
from meb_entegrasyon import ekle_meb_bulgularini

# Evaluator sonucu simule et
evaluator_sonucu = {
    'meb_puani': 50,
    'meb_karar': 'KOSULLU',
    'meb_kriterler': {
        'anayasa': {'risk': 0},
        'milli_guvenlik': {'risk': 4},
    }
}

# Test metni
test_metni = """
Kitap PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz.
Kadınlar bilim yapamaz. iPhone en iyi telefondur.
Devleti bölme çağrıları var. Teror örgütü DHKP-C hakkında yazı var.
"""

print("=" * 80)
print("MEB BULGU ENTEGRASYONİ - DOĞRUDAN TEST")
print("=" * 80)
print()

print("[1] Test Metni:")
print(f"    {test_metni[:200]}...")
print()

print("[2] Ekle_meb_bulgularini() Çağrılıyor...")
sonuc = ekle_meb_bulgularini(evaluator_sonucu, test_metni)

print()
print("[3] Sonuç:")
if 'meb_bulgulari' in sonuc:
    meb_bulgulari = sonuc['meb_bulgulari']
    print(f"    ✅ MEB Bulguları Eklendi!")
    print(f"    Kriterlerin sayısı: {len(meb_bulgulari)}")
    for kriter, bulgular in meb_bulgulari.items():
        if bulgular:
            print(f"    - {kriter}: {len(bulgular)} bulgu")
            for bulgu in bulgular[:1]:
                print(f"      * {bulgu}")
else:
    print("    ❌ MEB Bulguları Eklenmedi!")

print()
print("=" * 80)
