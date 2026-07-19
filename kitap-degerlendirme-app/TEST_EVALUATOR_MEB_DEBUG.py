#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluator ile Tam Entegrasyon Test
"""

from evaluator_maarif import MaarifDegerlendiricisi

# Test metni (riskli içerik)
test_kitap = """
Kitap PKK'nın direniş mücadelesinden bahsediyor. Siz de katılabilirsiniz.
Kadınlar bilim yapamaz. iPhone en iyi telefondur.
Devleti bölme çağrıları var. Teror örgütü DHKP-C hakkında yazı var.
"""

print("=" * 80)
print("EVALUATOR İLE TAM ENTEGRASYON - DEBUG TEST")
print("=" * 80)
print()

evaluator = MaarifDegerlendiricisi()
print("[1] Analiz yapılıyor...")
sonuc = evaluator.analiz_yap(test_kitap, profil="hibrit", yas_grubu="8-10")

print()
print("[2] Sonuçlar:")
print(f"    - Final Skor: {sonuc['final_skor']}/100")
print(f"    - MEB Puanı: {sonuc['meb_degerlendirmesi']['meb_puani']}/100")

print()
print("[3] MEB Bulgularının Kontrol Ediliyor...")
if 'meb_bulgulari' in sonuc['meb_degerlendirmesi']:
    meb_bulgulari = sonuc['meb_degerlendirmesi']['meb_bulgulari']
    print(f"    ✅ MEB Bulguları var! Kriter sayısı: {len(meb_bulgulari)}")
    
    for kriter, bulgular in meb_bulgulari.items():
        if bulgular:
            print(f"       - {kriter}: {len(bulgular)} bulgu")
else:
    print("    ❌ MEB Bulguları yok")

print()

# Derinlemesine kontrol
print("[4] Derinlemesine Kontrol (meb_degerlendirmesi keys):")
print(f"    {list(sonuc['meb_degerlendirmesi'].keys())}")

print()
print("=" * 80)
